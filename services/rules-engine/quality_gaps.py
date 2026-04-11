"""Deterministic quality gap evaluation.

Each rule is a pure function over (protocol, answers, emr_history) that
returns either a gap dict or None. Rules are registered by id so protocols
can opt into them via quality_gap_rules.
"""

from typing import Callable, Dict, List, Optional


GapRule = Callable[[dict, dict, dict], Optional[dict]]

_REGISTRY: Dict[str, GapRule] = {}


def register(rule_id: str):
    def _decorator(fn: GapRule) -> GapRule:
        _REGISTRY[rule_id] = fn
        return fn
    return _decorator


@register("statin_gap_if_cad_or_diabetes")
def _statin_gap_if_cad_or_diabetes(protocol, answers, emr_history):
    conditions = emr_history.get("conditions", []) or []
    meds = emr_history.get("meds", []) or []
    needs = any(c in conditions for c in ("coronary_artery_disease", "type_2_diabetes", "diabetes"))
    on_statin = any("statin" in m.lower() for m in meds)
    if needs and not on_statin:
        return {
            "id": "statin_gap_if_cad_or_diabetes",
            "message": "Patient has CAD/diabetes without a statin on med list.",
        }
    return None


@register("bp_control_gap_if_hypertension")
def _bp_control_gap_if_hypertension(protocol, answers, emr_history):
    conditions = emr_history.get("conditions", []) or []
    vitals = emr_history.get("vitals", {}) or {}
    if "hypertension" not in conditions:
        return None
    bp = vitals.get("blood_pressure", "")
    try:
        systolic = int(str(bp).split("/")[0])
    except (ValueError, IndexError):
        return None
    if systolic >= 140:
        return {
            "id": "bp_control_gap_if_hypertension",
            "message": f"Hypertensive with uncontrolled BP ({bp}).",
        }
    return None


@register("tobacco_cessation_if_smoker")
def _tobacco_cessation_if_smoker(protocol, answers, emr_history):
    social = emr_history.get("social_history", {}) or {}
    if social.get("tobacco") in ("current", "daily"):
        return {
            "id": "tobacco_cessation_if_smoker",
            "message": "Current tobacco use — offer cessation counseling.",
        }
    return None


def evaluate_quality_gaps(protocol: dict, answers: dict, emr_history: dict) -> List[dict]:
    gaps: List[dict] = []
    for rule_id in protocol.get("quality_gap_rules", []):
        rule = _REGISTRY.get(rule_id)
        if not rule:
            continue
        result = rule(protocol, answers, emr_history)
        if result:
            gaps.append(result)
    return gaps
