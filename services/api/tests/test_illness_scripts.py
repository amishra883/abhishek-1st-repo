"""Illness-script-driven tests for the smart intake pipeline.

Each test is parametrized over ALL_SCRIPTS.  The mock LLM returns the
script's golden outputs so we can validate the full pipeline shape
and deterministic rules.  When Claude Enterprise is available, swap
`_make_golden_llm` for a real LLM caller and the `_semantic_*` helpers
become live contract tests.

Run:  pytest api/tests/test_illness_scripts.py -v
"""

import pytest
from fastapi.testclient import TestClient

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.app.main import app
from api.app.routes import set_llm_call, set_emr_adapter
from emr_adapter.base import BaseEMRAdapter
from illness_scripts.scripts import ALL_SCRIPTS, IllnessScript


class ScriptEMRAdapter(BaseEMRAdapter):
    def __init__(self, emr_history: dict):
        self._history = emr_history

    def fetch_relevant_history(self, patient_id: str, fetch_plan: dict) -> dict:
        return self._history


SCRIPT_IDS = [s.id for s in ALL_SCRIPTS]

OUTPUT_REQUIRED_KEYS = {
    "complaint_protocol",
    "patient_answers",
    "relevant_emr_history",
    "red_flags",
    "quality_gaps",
    "summary",
    "recommendations",
    "patient_handout",
}

SUMMARY_REQUIRED_KEYS = {"hpi", "key_positives", "key_negatives", "relevant_history", "priority"}

RECOMMENDATION_REQUIRED_KEYS = {
    "treatment_considerations",
    "patient_education",
    "preventive_measures",
    "quality_gap_prompts",
}


def _make_golden_llm(script: IllnessScript):
    def _llm(system_prompt: str, context: dict) -> dict:
        if "complaint_protocol" in context:
            return script.golden_summary
        return script.golden_recommendation
    return _llm


@pytest.fixture(params=ALL_SCRIPTS, ids=SCRIPT_IDS)
def script(request):
    return request.param


@pytest.fixture
def result(script):
    set_llm_call(_make_golden_llm(script))
    set_emr_adapter(ScriptEMRAdapter(script.emr_history))
    client = TestClient(app)
    resp = client.post("/intake/process", json={
        "patient_id": script.patient_id,
        "chief_complaint": script.chief_complaint,
        "answers": script.answers,
    })
    set_llm_call(None)
    from emr_adapter.base import MockEMRAdapter
    set_emr_adapter(MockEMRAdapter())
    assert resp.status_code == 200, f"Script {script.id} failed: {resp.text}"
    return resp.json(), script


# -----------------------------------------------------------------------
# Schema conformance — every script must produce the full output shape
# -----------------------------------------------------------------------

class TestOutputConformance:
    def test_top_level_keys(self, result):
        data, _ = result
        assert set(data.keys()) == OUTPUT_REQUIRED_KEYS

    def test_summary_keys(self, result):
        data, _ = result
        assert set(data["summary"].keys()) >= SUMMARY_REQUIRED_KEYS

    def test_recommendation_keys(self, result):
        data, _ = result
        assert set(data["recommendations"].keys()) >= RECOMMENDATION_REQUIRED_KEYS

    def test_handout_keys(self, result):
        data, _ = result
        assert set(data["patient_handout"].keys()) == {"html", "education", "quality_gap_prompts"}

    def test_red_flags_are_list_of_dicts(self, result):
        data, _ = result
        assert isinstance(data["red_flags"], list)
        for flag in data["red_flags"]:
            assert isinstance(flag, dict)
            assert {"id", "severity", "patient_message"} == set(flag.keys())

    def test_quality_gaps_are_list_of_dicts(self, result):
        data, _ = result
        assert isinstance(data["quality_gaps"], list)
        for gap in data["quality_gaps"]:
            assert isinstance(gap, dict)
            assert {"id", "message"} == set(gap.keys())


# -----------------------------------------------------------------------
# Deterministic rule correctness — red flags and quality gaps
# -----------------------------------------------------------------------

class TestRedFlagCorrectness:
    def test_expected_red_flags_present(self, result):
        data, script = result
        actual_ids = sorted([f["id"] for f in data["red_flags"]])
        expected_ids = sorted(script.expected_red_flag_ids)
        assert actual_ids == expected_ids, (
            f"Script {script.id}: expected flags {expected_ids}, got {actual_ids}"
        )

    def test_urgent_scripts_have_red_flags(self, result):
        data, script = result
        if script.golden_summary.get("priority") == "urgent" and script.expected_red_flag_ids:
            assert len(data["red_flags"]) > 0

    def test_routine_scripts_have_no_red_flags(self, result):
        data, script = result
        if script.golden_summary.get("priority") == "routine":
            assert data["red_flags"] == []


class TestQualityGapCorrectness:
    def test_expected_quality_gaps_present(self, result):
        data, script = result
        actual_ids = sorted([g["id"] for g in data["quality_gaps"]])
        expected_ids = sorted(script.expected_quality_gap_ids)
        assert actual_ids == expected_ids, (
            f"Script {script.id}: expected gaps {expected_ids}, got {actual_ids}"
        )


# -----------------------------------------------------------------------
# Summary agent contract
# -----------------------------------------------------------------------

class TestSummaryContract:
    def test_hpi_is_nonempty_string(self, result):
        data, _ = result
        assert isinstance(data["summary"]["hpi"], str)
        assert len(data["summary"]["hpi"]) > 0

    def test_priority_is_valid(self, result):
        data, _ = result
        assert data["summary"]["priority"] in ("urgent", "routine", "emergent")

    def test_key_positives_are_list(self, result):
        data, _ = result
        assert isinstance(data["summary"]["key_positives"], list)

    def test_key_negatives_are_list(self, result):
        data, _ = result
        assert isinstance(data["summary"]["key_negatives"], list)

    def test_relevant_history_are_list(self, result):
        data, _ = result
        assert isinstance(data["summary"]["relevant_history"], list)

    def test_summary_contains_required_terms(self, result):
        data, script = result
        summary_text = _flatten_to_text(data["summary"])
        for term in script.summary_must_contain:
            assert term.lower() in summary_text.lower(), (
                f"Script {script.id}: summary missing required term '{term}'"
            )

    def test_summary_excludes_forbidden_terms(self, result):
        data, script = result
        summary_text = _flatten_to_text(data["summary"])
        for term in script.summary_must_not_contain:
            assert term.lower() not in summary_text.lower(), (
                f"Script {script.id}: summary contains forbidden term '{term}'"
            )

    def test_no_diagnosis_in_summary(self, result):
        data, _ = result
        summary_text = _flatten_to_text(data["summary"])
        for phrase in ["diagnosis is", "diagnosed with", "confirm diagnosis"]:
            assert phrase not in summary_text.lower()

    def test_no_treatment_in_summary(self, result):
        data, _ = result
        summary_text = _flatten_to_text(data["summary"])
        for phrase in ["prescribe", "start treatment", "order medication"]:
            assert phrase not in summary_text.lower()


# -----------------------------------------------------------------------
# Recommendation agent contract
# -----------------------------------------------------------------------

class TestRecommendationContract:
    def test_treatment_considerations_are_list(self, result):
        data, _ = result
        assert isinstance(data["recommendations"]["treatment_considerations"], list)
        assert len(data["recommendations"]["treatment_considerations"]) > 0

    def test_patient_education_are_list(self, result):
        data, _ = result
        assert isinstance(data["recommendations"]["patient_education"], list)
        assert len(data["recommendations"]["patient_education"]) > 0

    def test_preventive_measures_are_list(self, result):
        data, _ = result
        assert isinstance(data["recommendations"]["preventive_measures"], list)

    def test_quality_gap_prompts_are_list(self, result):
        data, _ = result
        assert isinstance(data["recommendations"]["quality_gap_prompts"], list)

    def test_recommendations_contain_required_terms(self, result):
        data, script = result
        rec_text = _flatten_to_text(data["recommendations"])
        for term in script.recommendation_must_contain:
            assert term.lower() in rec_text.lower(), (
                f"Script {script.id}: recommendations missing required term '{term}'"
            )

    def test_recommendations_exclude_forbidden_terms(self, result):
        data, script = result
        rec_text = _flatten_to_text(data["recommendations"])
        for term in script.recommendation_must_not_contain:
            assert term.lower() not in rec_text.lower(), (
                f"Script {script.id}: recommendations contain forbidden term '{term}'"
            )

    def test_no_final_diagnosis_in_recommendations(self, result):
        data, _ = result
        rec_text = _flatten_to_text(data["recommendations"])
        for phrase in ["final diagnosis", "definitive diagnosis", "diagnosed with"]:
            assert phrase not in rec_text.lower()

    def test_no_order_placement_in_recommendations(self, result):
        data, _ = result
        rec_text = _flatten_to_text(data["recommendations"])
        for phrase in ["order placed", "medication ordered", "prescription sent"]:
            assert phrase not in rec_text.lower()


# -----------------------------------------------------------------------
# Handout integration
# -----------------------------------------------------------------------

class TestHandoutIntegration:
    def test_handout_html_is_valid(self, result):
        data, _ = result
        html = data["patient_handout"]["html"]
        assert "<html>" in html
        assert "</html>" in html

    def test_handout_contains_hpi_content(self, result):
        data, script = result
        html = data["patient_handout"]["html"]
        assert script.golden_summary["hpi"][:20] in html

    def test_handout_warning_signs_match_red_flags(self, result):
        data, script = result
        html = data["patient_handout"]["html"]
        for flag_id in script.expected_red_flag_ids:
            flag = next(f for f in data["red_flags"] if f["id"] == flag_id)
            assert flag["patient_message"] in html

    def test_handout_education_matches_recommendations(self, result):
        data, _ = result
        assert data["patient_handout"]["education"] == data["recommendations"]["patient_education"]


# -----------------------------------------------------------------------
# Cross-script consistency
# -----------------------------------------------------------------------

class TestCrossScriptConsistency:
    def test_urgent_scripts_have_urgent_priority(self, result):
        data, script = result
        if script.expected_red_flag_ids:
            assert data["summary"]["priority"] == "urgent"

    def test_routine_scripts_have_routine_priority(self, result):
        data, script = result
        if not script.expected_red_flag_ids and script.golden_summary["priority"] == "routine":
            assert data["summary"]["priority"] == "routine"

    def test_quality_gap_prompts_reflect_detected_gaps(self, result):
        data, script = result
        if script.expected_quality_gap_ids:
            assert len(data["recommendations"]["quality_gap_prompts"]) > 0


# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------

def _flatten_to_text(d: dict) -> str:
    parts = []
    for v in d.values():
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    parts.append(item)
    return " ".join(parts)
