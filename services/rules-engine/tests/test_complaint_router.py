import pytest
from complaint_router import load_protocol, route_complaint


class TestLoadProtocol:
    def test_loads_chest_pain(self):
        protocol = load_protocol("chest_pain")
        assert protocol["id"] == "chest_pain"
        assert "questions" in protocol
        assert "red_flags" in protocol

    def test_loads_urinary_symptoms(self):
        protocol = load_protocol("urinary_symptoms")
        assert protocol["id"] == "urinary_symptoms"

    def test_raises_on_nonexistent_protocol(self):
        with pytest.raises(FileNotFoundError):
            load_protocol("nonexistent_protocol")


class TestRouteComplaint:
    def test_routes_chest_pain(self):
        protocol = route_complaint("I have chest pain")
        assert protocol is not None
        assert protocol["id"] == "chest_pain"

    def test_routes_chest_pressure(self):
        protocol = route_complaint("chest pressure")
        assert protocol is not None
        assert protocol["id"] == "chest_pain"

    def test_routes_case_insensitive(self):
        protocol = route_complaint("CHEST PAIN")
        assert protocol is not None
        assert protocol["id"] == "chest_pain"

    def test_routes_with_surrounding_whitespace(self):
        protocol = route_complaint("  chest pain  ")
        assert protocol is not None
        assert protocol["id"] == "chest_pain"

    def test_routes_urinary_symptoms(self):
        protocol = route_complaint("burning urination")
        assert protocol is not None
        assert protocol["id"] == "urinary_symptoms"

    def test_routes_uti_keyword(self):
        protocol = route_complaint("I think I have a uti")
        assert protocol is not None
        assert protocol["id"] == "urinary_symptoms"

    def test_returns_none_for_unmatched_complaint(self):
        protocol = route_complaint("my elbow hurts")
        assert protocol is None
