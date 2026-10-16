---
name: rls-onboarding-wizard
description: "Build OpenClaw read-access onboarding packages with verified sender IDs, department and role mappings, default-deny rules, source-permission reminders, and positive/negative test cases. Use for client knowledge, records, or internal database access planning; not for applying database RLS or third-party platform permissions."
---

# RLS Onboarding Wizard

Use this skill to create a client-specific OpenClaw read-access onboarding package.

## Scope

Focus v1.1 on OpenClaw internal database / knowledge / records **read-access decisions**.
This is a defense-in-depth workflow, not database row-level security. Do not auto-configure database policies, Discord, Notion, Google Drive, or Google Sheets permissions. Keep source-system permissions authoritative and mention them as required manual controls.

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
   - positive, wrong-role, cross-department, revoked-ID, and pending-ID tests listed
6. Use plain-language unauthorized reply:
   > 這份資料需要主管或資料負責人先同意，我現在不能直接提供。你可以請主管授權，或讓我幫你整理一份不含敏感內容的摘要。

## Key rules

- Client names are parameters, never hard-coded.
- Resolve a person from verified Discord numeric user ID or OpenClaw sender ID. Display names, nicknames, email addresses, and plain-text mentions are not authorization evidence.
- Unknown, conflicting, revoked, or `pending_id` identities are denied all governed internal data by default.
- Use only three data layers in v1: company shared, department general, department sensitive.
- Formal roles: executive owner, department lead, department member, AI consultant.
- Data owner is not a formal role in v1; use it only as a plain-language authorization concept.
- AI consultant can read company shared knowledge and assigned-department general data for troubleshooting; unassigned department general and all department sensitive data are denied by default.
- Executive owner can read all layers and manage permissions.
- Explicit exceptions must identify the approver, person, department, data layer, reason, and expiry. Expired or incomplete grants do not authorize access.
- OpenClaw-side rules never expand access beyond the source database, Discord, Notion, Drive, or other authoritative platform permissions.
- Personalization writes are allowed for self: tone, style, persona preference, personal non-sensitive memory.
- Official data writes are not part of v1 main flow.
- Never store raw sensitive data in memory: salary, customer PII, credentials, contract details, payment details, medical/beauty records.

## Bundled resources

- `references/baseline.md` — permission model and data layers.
- `references/wizard-questions.md` — step-by-step interview script.
- `assets/templates/` — output file templates.
- `scripts/generate_package.py` — creates a starter package from parameters.
