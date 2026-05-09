import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest
from ai_orchestrator.summary_agent import validate_summary, build_summary, load_prompt
from ai_orchestrator.recommendation_agent import (
    validate_recommendation,
    build_recommendation,
    load_prompt as load_rec_prompt,
)


class TestSummaryValidator:
    def test_accepts_valid_payload(self):
        payload = {
            "hpi": "Patient reports chest pain.",
            "key_positives": ["pressure quality"],
            "key_negatives": ["no fever"],
            "relevant_history": ["hypertension"],
            "priority": "urgent",
        }
        result = validate_summary(payload)
        assert result == payload

    def test_rejects_missing_key(self):
        payload = {
            "hpi": "Patient reports chest pain.",
            "key_positives": ["pressure quality"],
        }
        with pytest.raises(ValueError, match="missing required keys"):
            validate_summary(payload)

    def test_rejects_empty_dict(self):
        with pytest.raises(ValueError):
            validate_summary({})

    def test_allows_extra_keys(self):
        payload = {
            "hpi": "text",
            "key_positives": [],
            "key_negatives": [],
            "relevant_history": [],
            "priority": "routine",
            "extra_field": "value",
        }
        result = validate_summary(payload)
        assert "extra_field" in result


class TestRecommendationValidator:
    def test_accepts_valid_payload(self):
        payload = {
            "treatment_considerations": ["eval"],
            "patient_education": ["hydrate"],
            "preventive_measures": ["screening"],
            "quality_gap_prompts": [],
        }
        result = validate_recommendation(payload)
        assert result == payload

    def test_rejects_missing_key(self):
        payload = {"treatment_considerations": ["eval"]}
        with pytest.raises(ValueError, match="missing required keys"):
            validate_recommendation(payload)


class TestSummaryPrompt:
    def test_prompt_loads(self):
        text = load_prompt()
        assert "hpi" in text
        assert "key_positives" in text

    def test_prompt_forbids_diagnosis(self):
        text = load_prompt()
        assert "no diagnosis" in text


class TestRecommendationPrompt:
    def test_prompt_loads(self):
        text = load_rec_prompt()
        assert "treatment_considerations" in text

    def test_prompt_forbids_orders(self):
        text = load_rec_prompt()
        assert "do not place orders" in text


class TestBuildSummaryWithMockLLM:
    def test_returns_validated_output(self):
        mock_output = {
            "hpi": "Patient presents with chest pain.",
            "key_positives": ["pressure"],
            "key_negatives": ["no fever"],
            "relevant_history": ["htn"],
            "priority": "urgent",
        }

        def mock_llm(prompt, context):
            return mock_output

        result = build_summary(
            complaint_protocol={"id": "test"},
            patient_answers={"quality": "Pressure"},
            relevant_emr_history={},
            red_flags=[],
            llm_call=mock_llm,
        )
        assert result == mock_output

    def test_raises_on_invalid_llm_output(self):
        def bad_llm(prompt, context):
            return {"hpi": "text only"}

        with pytest.raises(ValueError):
            build_summary({}, {}, {}, [], llm_call=bad_llm)


class TestBuildRecommendationWithMockLLM:
    def test_returns_validated_output(self):
        mock_output = {
            "treatment_considerations": ["eval"],
            "patient_education": ["hydrate"],
            "preventive_measures": ["screening"],
            "quality_gap_prompts": [],
        }

        def mock_llm(prompt, context):
            return mock_output

        result = build_recommendation(
            summary={"hpi": "text"},
            relevant_emr_history={},
            quality_gaps=[],
            llm_call=mock_llm,
        )
        assert result == mock_output

    def test_raises_on_invalid_llm_output(self):
        def bad_llm(prompt, context):
            return {"treatment_considerations": ["eval"]}

        with pytest.raises(ValueError):
            build_recommendation({}, {}, [], llm_call=bad_llm)
