import sys
from pathlib import Path

services_dir = str(Path(__file__).resolve().parent)
if services_dir not in sys.path:
    sys.path.insert(0, services_dir)
