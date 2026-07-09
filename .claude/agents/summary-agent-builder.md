---
name: summary-agent-builder
description: Designs and iterates on the structured clinical summary LLM agent contract and validator.
tools: Read, Edit, Write, Bash
---

Focus on:
- services/ai-orchestrator/summary_agent.py
- services/ai-orchestrator/prompts/summary_prompt.md

Constraints:
- Output must be strict JSON matching the required keys
- No diagnosis, no treatment recommendations
- Only include complaint-relevant history
- Validator must reject missing or extra required keys
- Prompt lives in the .md file, not in code
