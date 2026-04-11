---
name: generate-complaint-protocol
description: Create or update a YAML complaint protocol with deterministic red flags, EMR relevance mapping, and quality gap rules.
---

Requirements:
- Follow packages/complaint-protocols schema
- Include trigger, questions, red_flags, emr_relevance, quality_gap_rules
- Keep triage logic deterministic
- Do not include treatment advice
- Preserve existing IDs when editing
