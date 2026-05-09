import pytest
from red_flags import evaluate_red_flags


class TestChestPainRedFlags:
    def test_acs_pattern_triggers_when_all_conditions_met(self, chest_pain_protocol):
        answers = {
            "quality": "Pressure",
            "sob": "Yes",
            "radiation": ["Left arm", "Jaw"],
        }
        flags = evaluate_red_flags(chest_pain_protocol, answers)
        assert len(flags) == 1
        assert flags[0]["id"] == "possible_acs_pattern"
        assert flags[0]["severity"] == "urgent"
        assert "patient_message" in flags[0]

    def test_acs_pattern_triggers_with_single_matching_radiation(self, chest_pain_protocol):
        answers = {
            "quality": "Pressure",
            "sob": "Yes",
            "radiation": ["Back"],
        }
        flags = evaluate_red_flags(chest_pain_protocol, answers)
        assert len(flags) == 1
        assert flags[0]["id"] == "possible_acs_pattern"

    def test_acs_pattern_does_not_trigger_wrong_quality(self, chest_pain_protocol):
        answers = {
            "quality": "Sharp",
            "sob": "Yes",
            "radiation": ["Left arm"],
        }
        flags = evaluate_red_flags(chest_pain_protocol, answers)
        assert flags == []

    def test_acs_pattern_does_not_trigger_no_sob(self, chest_pain_protocol):
        answers = {
            "quality": "Pressure",
            "sob": "No",
            "radiation": ["Left arm"],
        }
        flags = evaluate_red_flags(chest_pain_protocol, answers)
        assert flags == []

    def test_acs_pattern_does_not_trigger_non_matching_radiation(self, chest_pain_protocol):
        answers = {
            "quality": "Pressure",
            "sob": "Yes",
            "radiation": ["Does not spread"],
        }
        flags = evaluate_red_flags(chest_pain_protocol, answers)
        assert flags == []

    def test_acs_pattern_does_not_trigger_missing_radiation_field(self, chest_pain_protocol):
        answers = {
            "quality": "Pressure",
            "sob": "Yes",
        }
        flags = evaluate_red_flags(chest_pain_protocol, answers)
        assert flags == []

    def test_acs_pattern_does_not_trigger_empty_answers(self, chest_pain_protocol):
        flags = evaluate_red_flags(chest_pain_protocol, {})
        assert flags == []

    def test_flag_dict_shape(self, chest_pain_protocol):
        answers = {
            "quality": "Pressure",
            "sob": "Yes",
            "radiation": ["Jaw"],
        }
        flags = evaluate_red_flags(chest_pain_protocol, answers)
        flag = flags[0]
        assert set(flag.keys()) == {"id", "severity", "patient_message"}


class TestUrinaryRedFlags:
    def test_pyelonephritis_triggers_when_all_conditions_met(self, urinary_protocol):
        answers = {
            "flank_pain": "Yes",
            "fever": "Yes",
        }
        flags = evaluate_red_flags(urinary_protocol, answers)
        assert len(flags) == 1
        assert flags[0]["id"] == "possible_pyelonephritis"
        assert flags[0]["severity"] == "urgent"
        assert "patient_message" in flags[0]

    def test_pyelonephritis_does_not_trigger_no_flank_pain(self, urinary_protocol):
        answers = {
            "flank_pain": "No",
            "fever": "Yes",
        }
        flags = evaluate_red_flags(urinary_protocol, answers)
        assert flags == []

    def test_pyelonephritis_does_not_trigger_no_fever(self, urinary_protocol):
        answers = {
            "flank_pain": "Yes",
            "fever": "No",
        }
        flags = evaluate_red_flags(urinary_protocol, answers)
        assert flags == []

    def test_pyelonephritis_does_not_trigger_both_no(self, urinary_protocol):
        answers = {
            "flank_pain": "No",
            "fever": "No",
        }
        flags = evaluate_red_flags(urinary_protocol, answers)
        assert flags == []

    def test_pyelonephritis_does_not_trigger_empty_answers(self, urinary_protocol):
        flags = evaluate_red_flags(urinary_protocol, {})
        assert flags == []

    def test_flag_dict_shape(self, urinary_protocol):
        answers = {
            "flank_pain": "Yes",
            "fever": "Yes",
        }
        flags = evaluate_red_flags(urinary_protocol, answers)
        flag = flags[0]
        assert set(flag.keys()) == {"id", "severity", "patient_message"}


class TestRedFlagsWithNoProtocolFlags:
    def test_protocol_without_red_flags_returns_empty(self):
        protocol = {"id": "test", "questions": []}
        flags = evaluate_red_flags(protocol, {"anything": "here"})
        assert flags == []
