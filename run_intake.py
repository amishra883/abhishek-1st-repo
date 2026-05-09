#!/usr/bin/env python3
"""Smart Intake System — runnable demo and test harness.

Usage:
    python run_intake.py                    # run all 9 illness scripts
    python run_intake.py --script cp_acs_classic  # run one script
    python run_intake.py --list             # list available scripts
    python run_intake.py --validate         # run + validate contracts
"""

import argparse
import json
import sys
from pathlib import Path
from textwrap import indent

sys.path.insert(0, str(Path(__file__).resolve().parent / "services"))

from rules_engine.complaint_router import route_complaint
from rules_engine.red_flags import evaluate_red_flags
from rules_engine.emr_relevance import build_emr_fetch_plan
from rules_engine.quality_gaps import evaluate_quality_gaps
from ai_orchestrator.summary_agent import build_summary, REQUIRED_KEYS as SUMMARY_KEYS
from ai_orchestrator.recommendation_agent import build_recommendation, REQUIRED_KEYS as REC_KEYS
from print_service.renderer import render_handout

sys.path.insert(0, str(Path(__file__).resolve().parent / "services" / "api" / "tests"))
from illness_scripts.scripts import ALL_SCRIPTS, IllnessScript


DIVIDER = "─" * 72
PASS = "✓"
FAIL = "✗"


def run_pipeline(script: IllnessScript) -> dict:
    protocol = route_complaint(script.chief_complaint)
    if not protocol:
        return {"error": f"No protocol matched for '{script.chief_complaint}'"}

    red_flags = evaluate_red_flags(protocol, script.answers)
    fetch_plan = build_emr_fetch_plan(protocol)
    quality_gaps = evaluate_quality_gaps(protocol, script.answers, script.emr_history)

    def mock_llm(system_prompt: str, context: dict) -> dict:
        if "complaint_protocol" in context:
            return script.golden_summary
        return script.golden_recommendation

    summary = build_summary(
        complaint_protocol=protocol,
        patient_answers=script.answers,
        relevant_emr_history=script.emr_history,
        red_flags=red_flags,
        llm_call=mock_llm,
    )

    recommendations = build_recommendation(
        summary=summary,
        relevant_emr_history=script.emr_history,
        quality_gaps=quality_gaps,
        llm_call=mock_llm,
    )

    handout = render_handout(summary, recommendations, red_flags)

    return {
        "complaint_protocol": protocol["id"],
        "patient_answers": script.answers,
        "relevant_emr_history": script.emr_history,
        "red_flags": red_flags,
        "quality_gaps": quality_gaps,
        "summary": summary,
        "recommendations": recommendations,
        "patient_handout": handout,
    }


def validate_result(result: dict, script: IllnessScript) -> list:
    errors = []

    required_keys = {
        "complaint_protocol", "patient_answers", "relevant_emr_history",
        "red_flags", "quality_gaps", "summary", "recommendations", "patient_handout",
    }
    missing = required_keys - set(result.keys())
    if missing:
        errors.append(f"Missing top-level keys: {missing}")

    if "summary" in result:
        s = result["summary"]
        for k in SUMMARY_KEYS:
            if k not in s:
                errors.append(f"Summary missing key: {k}")

    if "recommendations" in result:
        r = result["recommendations"]
        for k in REC_KEYS:
            if k not in r:
                errors.append(f"Recommendation missing key: {k}")

    actual_flags = sorted([f["id"] for f in result.get("red_flags", [])])
    expected_flags = sorted(script.expected_red_flag_ids)
    if actual_flags != expected_flags:
        errors.append(f"Red flags: expected {expected_flags}, got {actual_flags}")

    actual_gaps = sorted([g["id"] for g in result.get("quality_gaps", [])])
    expected_gaps = sorted(script.expected_quality_gap_ids)
    if actual_gaps != expected_gaps:
        errors.append(f"Quality gaps: expected {expected_gaps}, got {actual_gaps}")

    def flatten(d):
        parts = []
        for v in d.values():
            if isinstance(v, str):
                parts.append(v)
            elif isinstance(v, list):
                parts.extend(item for item in v if isinstance(item, str))
        return " ".join(parts).lower()

    if "summary" in result:
        text = flatten(result["summary"])
        for term in script.summary_must_contain:
            if term.lower() not in text:
                errors.append(f"Summary missing required term: '{term}'")
        for term in script.summary_must_not_contain:
            if term.lower() in text:
                errors.append(f"Summary contains forbidden term: '{term}'")

    if "recommendations" in result:
        text = flatten(result["recommendations"])
        for term in script.recommendation_must_contain:
            if term.lower() not in text:
                errors.append(f"Recommendation missing required term: '{term}'")
        for term in script.recommendation_must_not_contain:
            if term.lower() in text:
                errors.append(f"Recommendation contains forbidden term: '{term}'")

    return errors


def print_result(script: IllnessScript, result: dict, errors: list = None):
    print(f"\n{DIVIDER}")
    print(f"  {script.id}: {script.label}")
    print(DIVIDER)

    if "error" in result:
        print(f"  ERROR: {result['error']}")
        return

    print(f"\n  Protocol:  {result['complaint_protocol']}")
    print(f"  Priority:  {result['summary']['priority']}")

    if result["red_flags"]:
        print(f"\n  Red Flags:")
        for f in result["red_flags"]:
            print(f"    [{f['severity'].upper()}] {f['id']}")
            print(f"      {f['patient_message']}")
    else:
        print(f"\n  Red Flags:  none")

    if result["quality_gaps"]:
        print(f"\n  Quality Gaps:")
        for g in result["quality_gaps"]:
            print(f"    - {g['id']}: {g['message']}")
    else:
        print(f"\n  Quality Gaps:  none")

    print(f"\n  Summary:")
    s = result["summary"]
    print(f"    HPI: {s['hpi']}")
    if s["key_positives"]:
        print(f"    Positives: {', '.join(s['key_positives'])}")
    if s["key_negatives"]:
        print(f"    Negatives: {', '.join(s['key_negatives'])}")
    if s["relevant_history"]:
        print(f"    History:")
        for h in s["relevant_history"]:
            print(f"      - {h}")

    print(f"\n  Recommendations:")
    r = result["recommendations"]
    if r["treatment_considerations"]:
        print(f"    Treatment:")
        for t in r["treatment_considerations"]:
            print(f"      - {t}")
    if r["patient_education"]:
        print(f"    Education:")
        for e in r["patient_education"]:
            print(f"      - {e}")
    if r["preventive_measures"]:
        print(f"    Prevention:")
        for p in r["preventive_measures"]:
            print(f"      - {p}")

    if errors is not None:
        print(f"\n  Validation:")
        if errors:
            for e in errors:
                print(f"    {FAIL} {e}")
        else:
            print(f"    {PASS} All contract checks passed")


def main():
    parser = argparse.ArgumentParser(description="Smart Intake System demo")
    parser.add_argument("--script", help="Run a specific script by ID")
    parser.add_argument("--list", action="store_true", help="List available scripts")
    parser.add_argument("--validate", action="store_true", help="Run contract validation")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    if args.list:
        print("\nAvailable illness scripts:\n")
        for s in ALL_SCRIPTS:
            flags = ", ".join(s.expected_red_flag_ids) if s.expected_red_flag_ids else "none"
            print(f"  {s.id:<30} {s.label}")
            print(f"  {'':30} priority={s.golden_summary['priority']}, flags={flags}")
        print()
        return

    scripts = ALL_SCRIPTS
    if args.script:
        scripts = [s for s in ALL_SCRIPTS if s.id == args.script]
        if not scripts:
            print(f"Unknown script: {args.script}")
            print(f"Available: {', '.join(s.id for s in ALL_SCRIPTS)}")
            sys.exit(1)

    total_errors = 0
    for script in scripts:
        result = run_pipeline(script)

        if args.json:
            output = {k: v for k, v in result.items() if k != "patient_handout"}
            output["patient_handout"] = {
                "education": result["patient_handout"]["education"],
                "quality_gap_prompts": result["patient_handout"]["quality_gap_prompts"],
            }
            print(json.dumps(output, indent=2))
            continue

        errors = validate_result(result, script) if args.validate else None
        print_result(script, result, errors)

        if errors:
            total_errors += len(errors)

    if not args.json:
        print(f"\n{DIVIDER}")
        print(f"  Ran {len(scripts)} illness script(s)")
        if args.validate:
            if total_errors == 0:
                print(f"  {PASS} All contract checks passed")
            else:
                print(f"  {FAIL} {total_errors} contract violation(s)")
        print(DIVIDER)
        print()

    if total_errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
