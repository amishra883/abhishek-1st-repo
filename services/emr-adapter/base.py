class BaseEMRAdapter:
    def fetch_relevant_history(self, patient_id: str, fetch_plan: dict) -> dict:
        raise NotImplementedError

class MockEMRAdapter(BaseEMRAdapter):
    def fetch_relevant_history(self, patient_id: str, fetch_plan: dict) -> dict:
        return {
            "conditions": ["hypertension", "type_2_diabetes"],
            "meds": ["lisinopril", "metformin", "atorvastatin"],
            "labs": {"a1c": "7.8", "ldl": "110"},
            "studies": ["stress_test_2023_normal"],
            "vitals": {"blood_pressure": "148/90", "heart_rate": "92"}
        }
