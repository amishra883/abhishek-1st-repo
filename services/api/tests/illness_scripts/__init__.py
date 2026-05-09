"""Illness script fixtures for agent intelligence testing.

Each script is a full clinical scenario: patient demographics, EMR history,
intake answers, and golden expected outputs for both the summary and
recommendation agents.  When running with a mock LLM the golden outputs ARE
the mock responses; when running against a real LLM they become the assertion
targets (semantic similarity or key-presence checks).
"""
