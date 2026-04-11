def build_emr_fetch_plan(protocol: dict) -> dict:
    emr = protocol.get("emr_relevance", {})
    return {
        "conditions": emr.get("conditions", []),
        "meds": emr.get("meds", []),
        "labs": emr.get("labs", []),
        "studies": emr.get("studies", []),
        "vitals": emr.get("vitals", []),
    }
