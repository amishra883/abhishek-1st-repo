import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from fastapi import APIRouter, HTTPException

from .schemas import IntakeRequest

_services_dir = str(Path(__file__).resolve().parents[2])
if _services_dir not in sys.path:
    sys.path.insert(0, _services_dir)

from rules_engine.complaint_router import route_complaint
from rules_engine.red_flags import evaluate_red_flags
from rules_engine.emr_relevance import build_emr_fetch_plan
from rules_engine.quality_gaps import evaluate_quality_gaps
from emr_adapter.base import BaseEMRAdapter, MockEMRAdapter
from ai_orchestrator.summary_agent import build_summary
from ai_orchestrator.recommendation_agent import build_recommendation
from print_service.renderer import render_handout

router = APIRouter()
_emr: BaseEMRAdapter = MockEMRAdapter()

_llm_call: Optional[Callable] = None


def set_llm_call(fn: Callable[[str, Dict[str, Any]], Dict[str, Any]]):
    global _llm_call
    _llm_call = fn


def set_emr_adapter(adapter: BaseEMRAdapter):
    global _emr
    _emr = adapter


def _get_llm_call() -> Callable:
    if _llm_call is None:
        raise RuntimeError("No LLM call configured. Call set_llm_call() first.")
    return _llm_call


@router.post("/intake/process")
def process_intake(payload: IntakeRequest):
    protocol = route_complaint(payload.chief_complaint)
    if not protocol:
        raise HTTPException(status_code=404, detail="No protocol matched")

    red_flags = evaluate_red_flags(protocol, payload.answers)
    fetch_plan = build_emr_fetch_plan(protocol)
    relevant_history = _emr.fetch_relevant_history(payload.patient_id, fetch_plan)
    quality_gaps = evaluate_quality_gaps(protocol, payload.answers, relevant_history)

    llm = _get_llm_call()

    summary = build_summary(
        complaint_protocol=protocol,
        patient_answers=payload.answers,
        relevant_emr_history=relevant_history,
        red_flags=red_flags,
        llm_call=llm,
    )

    recommendations = build_recommendation(
        summary=summary,
        relevant_emr_history=relevant_history,
        quality_gaps=quality_gaps,
        llm_call=llm,
    )

    patient_handout = render_handout(summary, recommendations, red_flags)

    return {
        "complaint_protocol": protocol["id"],
        "patient_answers": payload.answers,
        "relevant_emr_history": relevant_history,
        "red_flags": red_flags,
        "quality_gaps": quality_gaps,
        "summary": summary,
        "recommendations": recommendations,
        "patient_handout": patient_handout,
    }
