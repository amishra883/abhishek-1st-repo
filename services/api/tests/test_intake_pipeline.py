import pytest


CHEST_PAIN_ACS_PAYLOAD = {
    "patient_id": "P001",
    "chief_complaint": "chest pain",
    "answers": {
        "onset": "Today",
        "quality": "Pressure",
        "severity": 8,
        "radiation": ["Left arm", "Jaw"],
        "sob": "Yes",
        "exertional": "Yes",
    },
}

CHEST_PAIN_BENIGN_PAYLOAD = {
    "patient_id": "P002",
    "chief_complaint": "chest tightness",
    "answers": {
        "onset": "More than 1 week ago",
        "quality": "Dull ache",
        "severity": 3,
        "radiation": ["Does not spread"],
        "sob": "No",
        "exertional": "No",
    },
}

URINARY_PYELO_PAYLOAD = {
    "patient_id": "P003",
    "chief_complaint": "burning urination",
    "answers": {
        "onset": "1-2 days ago",
        "dysuria": "Yes",
        "frequency": "Yes",
        "hematuria": "No",
        "flank_pain": "Yes",
        "fever": "Yes",
    },
}

URINARY_SIMPLE_PAYLOAD = {
    "patient_id": "P004",
    "chief_complaint": "frequent urination",
    "answers": {
        "onset": "Within 1 week",
        "dysuria": "Yes",
        "frequency": "Yes",
        "hematuria": "No",
        "flank_pain": "No",
        "fever": "No",
    },
}


class TestOutputSchema:
    """Every response must match the output.schema.json contract."""

    REQUIRED_KEYS = {
        "complaint_protocol",
        "patient_answers",
        "relevant_emr_history",
        "red_flags",
        "quality_gaps",
        "summary",
        "recommendations",
        "patient_handout",
    }

    def test_chest_pain_response_has_all_keys(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_ACS_PAYLOAD)
        assert resp.status_code == 200
        assert self.REQUIRED_KEYS == set(resp.json().keys())

    def test_urinary_response_has_all_keys(self, client):
        resp = client.post("/intake/process", json=URINARY_PYELO_PAYLOAD)
        assert resp.status_code == 200
        assert self.REQUIRED_KEYS == set(resp.json().keys())


class TestProtocolRouting:
    def test_chest_pain_routes_correctly(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_ACS_PAYLOAD)
        assert resp.json()["complaint_protocol"] == "chest_pain"

    def test_urinary_routes_correctly(self, client):
        resp = client.post("/intake/process", json=URINARY_PYELO_PAYLOAD)
        assert resp.json()["complaint_protocol"] == "urinary_symptoms"

    def test_unmatched_complaint_returns_404(self, client):
        payload = {"patient_id": "P099", "chief_complaint": "sore elbow", "answers": {}}
        resp = client.post("/intake/process", json=payload)
        assert resp.status_code == 404


class TestRedFlagsIntegration:
    def test_acs_pattern_detected(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_ACS_PAYLOAD)
        flags = resp.json()["red_flags"]
        assert len(flags) == 1
        assert flags[0]["id"] == "possible_acs_pattern"
        assert flags[0]["severity"] == "urgent"

    def test_benign_chest_pain_no_flags(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_BENIGN_PAYLOAD)
        assert resp.json()["red_flags"] == []

    def test_pyelonephritis_detected(self, client):
        resp = client.post("/intake/process", json=URINARY_PYELO_PAYLOAD)
        flags = resp.json()["red_flags"]
        assert len(flags) == 1
        assert flags[0]["id"] == "possible_pyelonephritis"

    def test_simple_uti_no_flags(self, client):
        resp = client.post("/intake/process", json=URINARY_SIMPLE_PAYLOAD)
        assert resp.json()["red_flags"] == []


class TestQualityGapsIntegration:
    def test_bp_gap_detected_for_chest_pain(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_ACS_PAYLOAD)
        gaps = resp.json()["quality_gaps"]
        gap_ids = [g["id"] for g in gaps]
        assert "bp_control_gap_if_hypertension" in gap_ids

    def test_tobacco_gap_not_present_without_smoking_history(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_ACS_PAYLOAD)
        gaps = resp.json()["quality_gaps"]
        gap_ids = [g["id"] for g in gaps]
        assert "tobacco_cessation_if_smoker" not in gap_ids

    def test_statin_gap_not_present_when_on_statin(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_ACS_PAYLOAD)
        gaps = resp.json()["quality_gaps"]
        gap_ids = [g["id"] for g in gaps]
        assert "statin_gap_if_cad_or_diabetes" not in gap_ids


class TestSummaryAgent:
    def test_summary_has_required_keys(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_ACS_PAYLOAD)
        summary = resp.json()["summary"]
        assert set(summary.keys()) == {"hpi", "key_positives", "key_negatives", "relevant_history", "priority"}

    def test_summary_priority_reflects_red_flags(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_ACS_PAYLOAD)
        assert resp.json()["summary"]["priority"] == "urgent"

    def test_benign_summary_priority_is_routine(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_BENIGN_PAYLOAD)
        assert resp.json()["summary"]["priority"] == "routine"


class TestRecommendationAgent:
    def test_recommendations_have_required_keys(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_ACS_PAYLOAD)
        recs = resp.json()["recommendations"]
        assert set(recs.keys()) == {
            "treatment_considerations",
            "patient_education",
            "preventive_measures",
            "quality_gap_prompts",
        }

    def test_recommendations_lists_are_populated(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_ACS_PAYLOAD)
        recs = resp.json()["recommendations"]
        assert len(recs["treatment_considerations"]) > 0
        assert len(recs["patient_education"]) > 0
        assert len(recs["preventive_measures"]) > 0


class TestPatientHandout:
    def test_handout_contains_html(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_ACS_PAYLOAD)
        handout = resp.json()["patient_handout"]
        assert "html" in handout
        assert "<html>" in handout["html"]
        assert "Visit Summary" in handout["html"]

    def test_handout_includes_warning_signs_for_red_flags(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_ACS_PAYLOAD)
        html = resp.json()["patient_handout"]["html"]
        assert "urgent medical evaluation" in html

    def test_handout_has_no_warning_signs_when_benign(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_BENIGN_PAYLOAD)
        html = resp.json()["patient_handout"]["html"]
        assert "urgent medical evaluation" not in html

    def test_handout_includes_education(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_ACS_PAYLOAD)
        handout = resp.json()["patient_handout"]
        assert len(handout["education"]) > 0

    def test_handout_includes_quality_gap_prompts(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_ACS_PAYLOAD)
        handout = resp.json()["patient_handout"]
        assert isinstance(handout["quality_gap_prompts"], list)


class TestEMRHistory:
    def test_relevant_history_returned(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_ACS_PAYLOAD)
        emr = resp.json()["relevant_emr_history"]
        assert "conditions" in emr
        assert "meds" in emr
        assert "vitals" in emr

    def test_patient_answers_echoed_back(self, client):
        resp = client.post("/intake/process", json=CHEST_PAIN_ACS_PAYLOAD)
        assert resp.json()["patient_answers"] == CHEST_PAIN_ACS_PAYLOAD["answers"]


class TestValidation:
    def test_missing_patient_id_returns_422(self, client):
        payload = {"chief_complaint": "chest pain", "answers": {}}
        resp = client.post("/intake/process", json=payload)
        assert resp.status_code == 422

    def test_missing_chief_complaint_returns_422(self, client):
        payload = {"patient_id": "P001", "answers": {}}
        resp = client.post("/intake/process", json=payload)
        assert resp.status_code == 422

    def test_empty_body_returns_422(self, client):
        resp = client.post("/intake/process", json={})
        assert resp.status_code == 422
