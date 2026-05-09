import pytest
from emr_relevance import build_emr_fetch_plan


class TestChestPainEMRFetchPlan:
    def test_returns_all_expected_keys(self, chest_pain_protocol):
        plan = build_emr_fetch_plan(chest_pain_protocol)
        assert set(plan.keys()) == {"conditions", "meds", "labs", "studies", "vitals"}

    def test_conditions_match_protocol(self, chest_pain_protocol):
        plan = build_emr_fetch_plan(chest_pain_protocol)
        assert "coronary_artery_disease" in plan["conditions"]
        assert "hypertension" in plan["conditions"]
        assert "diabetes" in plan["conditions"]

    def test_meds_match_protocol(self, chest_pain_protocol):
        plan = build_emr_fetch_plan(chest_pain_protocol)
        assert "nitroglycerin" in plan["meds"]
        assert "statin" in plan["meds"]

    def test_labs_match_protocol(self, chest_pain_protocol):
        plan = build_emr_fetch_plan(chest_pain_protocol)
        assert "lipids" in plan["labs"]
        assert "a1c" in plan["labs"]

    def test_studies_match_protocol(self, chest_pain_protocol):
        plan = build_emr_fetch_plan(chest_pain_protocol)
        assert "ecg" in plan["studies"]
        assert "stress_test" in plan["studies"]

    def test_vitals_match_protocol(self, chest_pain_protocol):
        plan = build_emr_fetch_plan(chest_pain_protocol)
        assert "blood_pressure" in plan["vitals"]
        assert "oxygen_saturation" in plan["vitals"]


class TestUrinaryEMRFetchPlan:
    def test_returns_all_expected_keys(self, urinary_protocol):
        plan = build_emr_fetch_plan(urinary_protocol)
        assert set(plan.keys()) == {"conditions", "meds", "labs", "studies", "vitals"}

    def test_conditions_include_pregnancy(self, urinary_protocol):
        plan = build_emr_fetch_plan(urinary_protocol)
        assert "pregnancy" in plan["conditions"]
        assert "recurrent_uti" in plan["conditions"]

    def test_labs_include_urinalysis(self, urinary_protocol):
        plan = build_emr_fetch_plan(urinary_protocol)
        assert "urinalysis" in plan["labs"]
        assert "urine_culture" in plan["labs"]


class TestEMRFetchPlanWithEmptyProtocol:
    def test_missing_emr_relevance_returns_empty_lists(self):
        protocol = {"id": "test"}
        plan = build_emr_fetch_plan(protocol)
        assert plan == {
            "conditions": [],
            "meds": [],
            "labs": [],
            "studies": [],
            "vitals": [],
        }

    def test_partial_emr_relevance_fills_missing_keys(self):
        protocol = {"emr_relevance": {"conditions": ["asthma"]}}
        plan = build_emr_fetch_plan(protocol)
        assert plan["conditions"] == ["asthma"]
        assert plan["meds"] == []
        assert plan["labs"] == []
        assert plan["studies"] == []
        assert plan["vitals"] == []
