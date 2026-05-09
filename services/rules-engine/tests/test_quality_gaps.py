import pytest
from quality_gaps import evaluate_quality_gaps


class TestStatinGap:
    def test_triggers_for_cad_without_statin(self, chest_pain_protocol):
        emr = {"conditions": ["coronary_artery_disease"], "meds": ["metoprolol"]}
        gaps = evaluate_quality_gaps(chest_pain_protocol, {}, emr)
        statin_gaps = [g for g in gaps if g["id"] == "statin_gap_if_cad_or_diabetes"]
        assert len(statin_gaps) == 1
        assert "message" in statin_gaps[0]

    def test_triggers_for_diabetes_without_statin(self, chest_pain_protocol):
        emr = {"conditions": ["type_2_diabetes"], "meds": []}
        gaps = evaluate_quality_gaps(chest_pain_protocol, {}, emr)
        statin_gaps = [g for g in gaps if g["id"] == "statin_gap_if_cad_or_diabetes"]
        assert len(statin_gaps) == 1

    def test_does_not_trigger_when_on_statin(self, chest_pain_protocol):
        emr = {"conditions": ["coronary_artery_disease"], "meds": ["Atorvastatin 40mg"]}
        gaps = evaluate_quality_gaps(chest_pain_protocol, {}, emr)
        statin_gaps = [g for g in gaps if g["id"] == "statin_gap_if_cad_or_diabetes"]
        assert statin_gaps == []

    def test_does_not_trigger_without_qualifying_condition(self, chest_pain_protocol):
        emr = {"conditions": ["hypertension"], "meds": []}
        gaps = evaluate_quality_gaps(chest_pain_protocol, {}, emr)
        statin_gaps = [g for g in gaps if g["id"] == "statin_gap_if_cad_or_diabetes"]
        assert statin_gaps == []

    def test_gap_dict_shape(self, chest_pain_protocol):
        emr = {"conditions": ["coronary_artery_disease"], "meds": []}
        gaps = evaluate_quality_gaps(chest_pain_protocol, {}, emr)
        gap = [g for g in gaps if g["id"] == "statin_gap_if_cad_or_diabetes"][0]
        assert set(gap.keys()) == {"id", "message"}


class TestBPControlGap:
    def test_triggers_for_uncontrolled_bp(self, chest_pain_protocol):
        emr = {
            "conditions": ["hypertension"],
            "vitals": {"blood_pressure": "155/95"},
        }
        gaps = evaluate_quality_gaps(chest_pain_protocol, {}, emr)
        bp_gaps = [g for g in gaps if g["id"] == "bp_control_gap_if_hypertension"]
        assert len(bp_gaps) == 1
        assert "message" in bp_gaps[0]

    def test_does_not_trigger_for_controlled_bp(self, chest_pain_protocol):
        emr = {
            "conditions": ["hypertension"],
            "vitals": {"blood_pressure": "128/82"},
        }
        gaps = evaluate_quality_gaps(chest_pain_protocol, {}, emr)
        bp_gaps = [g for g in gaps if g["id"] == "bp_control_gap_if_hypertension"]
        assert bp_gaps == []

    def test_does_not_trigger_without_hypertension(self, chest_pain_protocol):
        emr = {
            "conditions": [],
            "vitals": {"blood_pressure": "180/100"},
        }
        gaps = evaluate_quality_gaps(chest_pain_protocol, {}, emr)
        bp_gaps = [g for g in gaps if g["id"] == "bp_control_gap_if_hypertension"]
        assert bp_gaps == []

    def test_does_not_trigger_when_bp_missing(self, chest_pain_protocol):
        emr = {"conditions": ["hypertension"], "vitals": {}}
        gaps = evaluate_quality_gaps(chest_pain_protocol, {}, emr)
        bp_gaps = [g for g in gaps if g["id"] == "bp_control_gap_if_hypertension"]
        assert bp_gaps == []

    def test_boundary_systolic_140_triggers(self, chest_pain_protocol):
        emr = {
            "conditions": ["hypertension"],
            "vitals": {"blood_pressure": "140/90"},
        }
        gaps = evaluate_quality_gaps(chest_pain_protocol, {}, emr)
        bp_gaps = [g for g in gaps if g["id"] == "bp_control_gap_if_hypertension"]
        assert len(bp_gaps) == 1

    def test_boundary_systolic_139_does_not_trigger(self, chest_pain_protocol):
        emr = {
            "conditions": ["hypertension"],
            "vitals": {"blood_pressure": "139/90"},
        }
        gaps = evaluate_quality_gaps(chest_pain_protocol, {}, emr)
        bp_gaps = [g for g in gaps if g["id"] == "bp_control_gap_if_hypertension"]
        assert bp_gaps == []


class TestTobaccoCessationGap:
    def test_triggers_for_current_smoker(self, chest_pain_protocol):
        emr = {"social_history": {"tobacco": "current"}}
        gaps = evaluate_quality_gaps(chest_pain_protocol, {}, emr)
        tobacco_gaps = [g for g in gaps if g["id"] == "tobacco_cessation_if_smoker"]
        assert len(tobacco_gaps) == 1

    def test_triggers_for_daily_smoker(self, chest_pain_protocol):
        emr = {"social_history": {"tobacco": "daily"}}
        gaps = evaluate_quality_gaps(chest_pain_protocol, {}, emr)
        tobacco_gaps = [g for g in gaps if g["id"] == "tobacco_cessation_if_smoker"]
        assert len(tobacco_gaps) == 1

    def test_does_not_trigger_for_former_smoker(self, chest_pain_protocol):
        emr = {"social_history": {"tobacco": "former"}}
        gaps = evaluate_quality_gaps(chest_pain_protocol, {}, emr)
        tobacco_gaps = [g for g in gaps if g["id"] == "tobacco_cessation_if_smoker"]
        assert tobacco_gaps == []

    def test_does_not_trigger_for_never_smoker(self, chest_pain_protocol):
        emr = {"social_history": {"tobacco": "never"}}
        gaps = evaluate_quality_gaps(chest_pain_protocol, {}, emr)
        tobacco_gaps = [g for g in gaps if g["id"] == "tobacco_cessation_if_smoker"]
        assert tobacco_gaps == []

    def test_does_not_trigger_when_social_history_missing(self, chest_pain_protocol):
        emr = {}
        gaps = evaluate_quality_gaps(chest_pain_protocol, {}, emr)
        tobacco_gaps = [g for g in gaps if g["id"] == "tobacco_cessation_if_smoker"]
        assert tobacco_gaps == []


class TestQualityGapsWithUnknownRules:
    def test_unknown_rule_ids_are_skipped(self):
        protocol = {"quality_gap_rules": ["nonexistent_rule"]}
        gaps = evaluate_quality_gaps(protocol, {}, {})
        assert gaps == []

    def test_protocol_without_quality_gap_rules_returns_empty(self):
        protocol = {"id": "test"}
        gaps = evaluate_quality_gaps(protocol, {}, {})
        assert gaps == []
