.PHONY: install test test-rules test-agents test-print test-api test-scripts test-quick

install:
	pip install -r requirements-test.txt

test:
	python -m pytest

test-rules:
	python -m pytest services/rules-engine/tests/

test-agents:
	python -m pytest services/ai-orchestrator/tests/

test-print:
	python -m pytest services/print-service/tests/

test-api:
	python -m pytest services/api/tests/test_intake_pipeline.py

test-scripts:
	python -m pytest services/api/tests/test_illness_scripts.py

test-quick:
	python -m pytest services/rules-engine/tests/ services/ai-orchestrator/tests/ services/print-service/tests/ services/api/tests/test_intake_pipeline.py
