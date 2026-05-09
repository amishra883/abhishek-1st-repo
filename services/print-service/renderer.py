from pathlib import Path
from typing import Any, Dict, List


TEMPLATE_PATH = Path(__file__).resolve().parent / "handout_template.html"


def _bullet_list(items: List[str]) -> str:
    return "\n".join(f"<li>{item}</li>" for item in items)


def render_handout(summary: dict, recommendations: dict, red_flags: list) -> Dict[str, Any]:
    template = TEMPLATE_PATH.read_text()

    summary_points = []
    if summary.get("hpi"):
        summary_points.append(summary["hpi"])
    for pos in summary.get("key_positives", []):
        summary_points.append(pos)

    next_steps = recommendations.get("treatment_considerations", [])

    warning_signs = [f["patient_message"] for f in red_flags]

    prevention = recommendations.get("preventive_measures", [])

    html = template
    html = html.replace("{{SUMMARY_POINTS}}", _bullet_list(summary_points))
    html = html.replace("{{NEXT_STEPS}}", _bullet_list(next_steps))
    html = html.replace("{{WARNING_SIGNS}}", _bullet_list(warning_signs))
    html = html.replace("{{PREVENTION}}", _bullet_list(prevention))

    return {
        "html": html,
        "education": recommendations.get("patient_education", []),
        "quality_gap_prompts": recommendations.get("quality_gap_prompts", []),
    }
