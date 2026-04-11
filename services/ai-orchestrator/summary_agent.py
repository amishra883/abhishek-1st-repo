"""Summary agent contract.

Wraps an LLM call that turns normalized intake + relevant EMR history into a
strict JSON summary. The actual LLM client is injected so this module stays
testable and swappable.
"""

from pathlib import Path
from typing import Any, Callable, Dict

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "summary_prompt.md"

REQUIRED_KEYS = ("hpi", "key_positives", "key_negatives", "relevant_history", "priority")


def load_prompt() -> str:
    return PROMPT_PATH.read_text()


def validate_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing = [k for k in REQUIRED_KEYS if k not in payload]
    if missing:
        raise ValueError(f"summary missing required keys: {missing}")
    return payload


def build_summary(
    complaint_protocol: dict,
    patient_answers: dict,
    relevant_emr_history: dict,
    red_flags: list,
    llm_call: Callable[[str, Dict[str, Any]], Dict[str, Any]],
) -> Dict[str, Any]:
    system_prompt = load_prompt()
    context = {
        "complaint_protocol": complaint_protocol,
        "patient_answers": patient_answers,
        "relevant_emr_history": relevant_emr_history,
        "red_flags": red_flags,
    }
    raw = llm_call(system_prompt, context)
    return validate_summary(raw)
