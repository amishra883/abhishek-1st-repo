---
name: write-rules-engine-tests
description: Author deterministic unit tests for the rules engine covering red flags, EMR relevance, and quality gaps.
---

Requirements:
- Place tests under services/rules-engine/tests
- Use pytest
- Cover each red flag's positive and negative branches
- Load protocols via services/rules-engine/complaint_router.load_protocol
- Never call an LLM from a rules-engine test
- Assert on dict shapes, not string formatting
