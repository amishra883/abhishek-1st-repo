from fastapi import APIRouter, HTTPException
from .schemas import IntakeRequest
from services.rules_engine.complaint_router import route_complaint
from services.rules_engine.red_flags import evaluate_red_flags
from services.rules_engine.emr_relevance import build_emr_fetch_plan
from services.emr_adapter.base import MockEMRAdapter

router = APIRouter()
emr = MockEMRAdapter()

@router.post("/intake/process")
def process_intake(payload: IntakeRequest):
    protocol = route_complaint(payload.chief_complaint)
    if not protocol:
        raise HTTPException(status_code=404, detail="No protocol matched")

    red_flags = evaluate_red_flags(protocol, payload.answers)
    fetch_plan = build_emr_fetch_plan(protocol)
    relevant_history = emr.fetch_relevant_history(payload.patient_id, fetch_plan)

    return {
        "complaint_protocol": protocol["id"],
        "patient_answers": payload.answers,
        "relevant_emr_history": relevant_history,
        "red_flags": red_flags,
        "quality_gaps": []
    }
