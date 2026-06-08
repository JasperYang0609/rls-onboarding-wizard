---
name: rls-onboarding-wizard
description: Build a reusable client RLS onboarding flow for OpenClaw internal database/knowledge read permissions. Use when setting up client-specific RLS matrices, department-by-department permission onboarding, Discord/OpenClaw sender ID mapping, safe baseline permissions, unauthorized reply rules, and handoff/checklist/test-case files for client deployments.
---

# RLS Onboarding Wizard

Use this skill to create a client-specific OpenClaw RLS onboarding package.

## Scope

Focus v1 on OpenClaw internal database / knowledge / records **read permissions**.
Do not auto-configure Discord, Notion, Google Drive, or Google Sheets permissions. Mention them only as manual reminders.

## Workflow

1. Collect launch parameters:
   - `client_name`
   - `client_slug`
   - `industry` optional
   - `default_template` default `safe_baseline`
   - `mode` default `openclaw_read_rls`
2. Apply the safe baseline from `references/baseline.md`.
3. Run the department closed-loop process from `references/wizard-questions.md`.
4. Generate files under `records/<client_slug>/`:
   - `rls_matrix.yaml`
   - `AGENTS_rls_addendum.md`
   - `onsite_rls_checklist.md`
   - `rls_test_cases.md`
   - `manual_platform_permissions.md`
5. Validate every department before moving to the next one:
   - department owner/lead known or marked as normal members
   - Discord numeric ID / OpenClaw sender_id captured or `pending_id`
   - data assigned to one of three layers: company shared, department general, department sensitive
   - positive, negative, and pending-ID tests listed
6. Use plain-language unauthorized reply:
   > 這份資料需要主管或資料負責人先同意，我現在不能直接提供。你可以請主管授權，或讓我幫你整理一份不含敏感內容的摘要。

## Key rules

- Client names are parameters, never hard-coded.
- Use only three data layers in v1: company shared, department general, department sensitive.
- Formal roles: executive owner, department lead, department member, AI consultant.
- Data owner is not a formal role in v1; use it only as a plain-language authorization concept.
- AI consultant can read company shared knowledge and department general data for troubleshooting; department sensitive is denied by default unless explicitly authorized.
- Executive owner can read all layers and manage permissions.
- Personalization writes are allowed for self: tone, style, persona preference, personal non-sensitive memory.
- Official data writes are not part of v1 main flow.
- Never store raw sensitive data in memory: salary, customer PII, credentials, contract details, payment details, medical/beauty records.

## Bundled resources

- `references/baseline.md` — permission model and data layers.
- `references/wizard-questions.md` — step-by-step interview script.
- `assets/templates/` — output file templates.
- `scripts/generate_package.py` — creates a starter package from parameters.
