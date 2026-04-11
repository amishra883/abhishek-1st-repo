from pathlib import Path
import yaml

PROTOCOL_DIR = Path(__file__).resolve().parents[2] / "packages" / "complaint-protocols"

def load_protocol(protocol_id: str):
    path = PROTOCOL_DIR / f"{protocol_id}.yaml"
    with open(path, "r") as f:
        return yaml.safe_load(f)

def route_complaint(chief_complaint: str):
    chief = chief_complaint.lower().strip()
    for file in PROTOCOL_DIR.glob("*.yaml"):
        with open(file, "r") as f:
            protocol = yaml.safe_load(f)
        for kw in protocol.get("trigger", {}).get("chief_complaint_keywords", []):
            if kw.lower() in chief:
                return protocol
    return None
