import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from complaint_router import load_protocol


@pytest.fixture
def chest_pain_protocol():
    return load_protocol("chest_pain")


@pytest.fixture
def urinary_protocol():
    return load_protocol("urinary_symptoms")
