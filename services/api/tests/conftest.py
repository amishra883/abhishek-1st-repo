import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.routes import set_llm_call


def mock_llm_call(system_prompt: str, context: dict) -> dict:
    if "hpi" not in str(system_prompt) and "treatment" not in str(system_prompt):
        raise ValueError(f"Unexpected prompt: {system_prompt[:80]}")

    if "complaint_protocol" in context:
        return {
            "hpi": "Patient presents with chief complaint.",
            "key_positives": ["symptom_a reported"],
            "key_negatives": ["symptom_b denied"],
            "relevant_history": ["hypertension", "type_2_diabetes"],
            "priority": "urgent" if context.get("red_flags") else "routine",
        }

    return {
        "treatment_considerations": ["Consider evaluation", "Monitor vitals"],
        "patient_education": ["Stay hydrated", "Follow up in 48 hours"],
        "preventive_measures": ["Annual screening", "Lifestyle modifications"],
        "quality_gap_prompts": [g["message"] for g in context.get("quality_gaps", [])],
    }


@pytest.fixture(autouse=True)
def _inject_mock_llm():
    set_llm_call(mock_llm_call)
    yield
    set_llm_call(None)


@pytest.fixture
def client():
    return TestClient(app)
