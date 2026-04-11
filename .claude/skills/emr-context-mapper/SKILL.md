---
name: emr-context-mapper
description: Map a complaint protocol's emr_relevance block to a read-only fetch plan the EMR adapter can execute.
---

Requirements:
- Read emr_relevance from the protocol
- Produce a fetch plan with conditions, meds, labs, studies, vitals
- Never emit writeback operations
- Keep field names stable; downstream code depends on them
- Add new categories by extending build_emr_fetch_plan in services/rules-engine/emr_relevance.py
