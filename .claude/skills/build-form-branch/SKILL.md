---
name: build-form-branch
description: Extend the dynamic intake form to support new question types and branching logic while keeping renderer config-driven.
---

Requirements:
- Edit apps/patient-web/components/DynamicForm.tsx and components/fields.tsx
- Keep the renderer purely data-driven from protocol JSON/YAML
- Support single_select, multi_select, scale; add new types by extending fields.tsx
- Branching rules live in the protocol, never hardcoded in the renderer
- Preserve accessibility: every field must have a label
- Do not add client-side clinical logic; red flags stay server-side
