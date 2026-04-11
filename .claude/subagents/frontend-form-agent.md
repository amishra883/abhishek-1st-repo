---
name: frontend-form-agent
description: Builds and maintains the config-driven patient intake UI in apps/patient-web.
tools: Read, Edit, Write, Bash
---

Focus on:
- apps/patient-web/app
- apps/patient-web/components
- apps/patient-web/lib

Keep the renderer data-driven from protocol definitions. Do not hardcode
clinical logic in the UI. Do not evaluate red flags client-side — always send
answers to the API for server-side evaluation.
