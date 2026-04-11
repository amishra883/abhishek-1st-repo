"""Recommendation agent contract.

Produces strict JSON with treatment considerations, patient education,
preventive measures, and quality-gap prompts. The LLM client is injected.
"""

from pathlib import Path
from typing import Any, Callable, Dict

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "recommendation_prompt.md"

REQUIRED_KEYS = (
    "treatment_considerations",
    "patient_education",
    "preventive_measures",
    "quality_gap_prompts",
)


def load_prompt() -> str:
    return PROMPT_PATH.read_text()


def validate_recommendation(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing = [k for k in REQUIRED_KEYS if k not in payload]
    if missing:
        raise ValueError(f"recommendation missing required keys: {missing}")
    return payload


def build_recommendation(
    summary: dict,
    relevant_emr_history: dict,
    quality_gaps: list,
    llm_call: Callable[[str, Dict[str, Any]], Dict[str, Any]],
) -> Dict[str, Any]:
    system_prompt = load_prompt()
    context = {
        "summary": summary,
        "relevant_emr_history": relevant_emr_history,
        "quality_gaps": quality_gaps,
    }
    raw = llm_call(system_prompt, context)
    return validate_recommendation(raw)
