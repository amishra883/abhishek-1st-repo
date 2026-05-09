import sys
from pathlib import Path

_services_dir = str(Path(__file__).resolve().parent)
if _services_dir not in sys.path:
    sys.path.insert(0, _services_dir)
