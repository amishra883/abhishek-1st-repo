from pydantic import BaseModel
from typing import Dict, Any

class IntakeRequest(BaseModel):
    patient_id: str
    chief_complaint: str
    answers: Dict[str, Any]
