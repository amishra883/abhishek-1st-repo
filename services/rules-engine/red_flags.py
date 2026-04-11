def _match_condition(answer_value, rule):
    if "equals" in rule:
        return answer_value == rule["equals"]
    if "includes_any" in rule:
        if not isinstance(answer_value, list):
            return False
        return any(v in answer_value for v in rule["includes_any"])
    return False

def evaluate_red_flags(protocol, answers):
    findings = []
    for flag in protocol.get("red_flags", []):
        when = flag.get("when", {})
        all_rules = when.get("all", [])
        passed = True
        for rule in all_rules:
            field = rule["field"]
            if not _match_condition(answers.get(field), rule):
                passed = False
                break
        if passed:
            findings.append({
                "id": flag["id"],
                "severity": flag["severity"],
                "patient_message": flag["patient_message"]
            })
    return findings
