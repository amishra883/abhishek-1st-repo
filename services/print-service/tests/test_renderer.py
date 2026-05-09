import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from print_service.renderer import render_handout


SAMPLE_SUMMARY = {
    "hpi": "Patient presents with chest pain, pressure quality.",
    "key_positives": ["radiation to left arm", "shortness of breath"],
    "key_negatives": ["no fever"],
    "relevant_history": ["hypertension"],
    "priority": "urgent",
}

SAMPLE_RECOMMENDATIONS = {
    "treatment_considerations": ["Obtain ECG", "Troponin levels"],
    "patient_education": ["Call 911 if symptoms worsen", "Avoid exertion"],
    "preventive_measures": ["Annual lipid panel", "BP monitoring"],
    "quality_gap_prompts": ["Uncontrolled BP noted"],
}

SAMPLE_RED_FLAGS = [
    {
        "id": "possible_acs_pattern",
        "severity": "urgent",
        "patient_message": "These symptoms may require urgent medical evaluation.",
    }
]


class TestRenderHandout:
    def test_returns_html_key(self):
        result = render_handout(SAMPLE_SUMMARY, SAMPLE_RECOMMENDATIONS, SAMPLE_RED_FLAGS)
        assert "html" in result
        assert isinstance(result["html"], str)

    def test_html_contains_structure(self):
        result = render_handout(SAMPLE_SUMMARY, SAMPLE_RECOMMENDATIONS, SAMPLE_RED_FLAGS)
        html = result["html"]
        assert "<html>" in html
        assert "Visit Summary" in html
        assert "What we discussed" in html
        assert "What to do next" in html
        assert "Important warning signs" in html
        assert "Prevention reminders" in html

    def test_html_includes_hpi(self):
        result = render_handout(SAMPLE_SUMMARY, SAMPLE_RECOMMENDATIONS, SAMPLE_RED_FLAGS)
        assert "chest pain" in result["html"]

    def test_html_includes_positives(self):
        result = render_handout(SAMPLE_SUMMARY, SAMPLE_RECOMMENDATIONS, SAMPLE_RED_FLAGS)
        assert "radiation to left arm" in result["html"]

    def test_html_includes_treatment_considerations(self):
        result = render_handout(SAMPLE_SUMMARY, SAMPLE_RECOMMENDATIONS, SAMPLE_RED_FLAGS)
        assert "Obtain ECG" in result["html"]

    def test_html_includes_warning_from_red_flags(self):
        result = render_handout(SAMPLE_SUMMARY, SAMPLE_RECOMMENDATIONS, SAMPLE_RED_FLAGS)
        assert "urgent medical evaluation" in result["html"]

    def test_html_includes_prevention(self):
        result = render_handout(SAMPLE_SUMMARY, SAMPLE_RECOMMENDATIONS, SAMPLE_RED_FLAGS)
        assert "Annual lipid panel" in result["html"]

    def test_education_returned_separately(self):
        result = render_handout(SAMPLE_SUMMARY, SAMPLE_RECOMMENDATIONS, SAMPLE_RED_FLAGS)
        assert result["education"] == SAMPLE_RECOMMENDATIONS["patient_education"]

    def test_quality_gap_prompts_returned(self):
        result = render_handout(SAMPLE_SUMMARY, SAMPLE_RECOMMENDATIONS, SAMPLE_RED_FLAGS)
        assert result["quality_gap_prompts"] == ["Uncontrolled BP noted"]

    def test_no_red_flags_produces_empty_warnings(self):
        result = render_handout(SAMPLE_SUMMARY, SAMPLE_RECOMMENDATIONS, [])
        assert "urgent medical evaluation" not in result["html"]

    def test_empty_summary_still_renders(self):
        empty_summary = {
            "hpi": "",
            "key_positives": [],
            "key_negatives": [],
            "relevant_history": [],
            "priority": "routine",
        }
        empty_recs = {
            "treatment_considerations": [],
            "patient_education": [],
            "preventive_measures": [],
            "quality_gap_prompts": [],
        }
        result = render_handout(empty_summary, empty_recs, [])
        assert "<html>" in result["html"]

    def test_result_dict_shape(self):
        result = render_handout(SAMPLE_SUMMARY, SAMPLE_RECOMMENDATIONS, SAMPLE_RED_FLAGS)
        assert set(result.keys()) == {"html", "education", "quality_gap_prompts"}
