# RLS Baseline

## v1.1 Scope

Handle only OpenClaw internal database / knowledge / records read-access decisions.
This package does not create database row-level security or change Discord / Notion / Google permissions. Those source controls remain authoritative.

## Decision order

1. Resolve the requester from a verified Discord numeric user ID or OpenClaw sender ID.
2. Deny if the identity is unknown, conflicting, revoked, or `pending_id`.
3. Confirm the source system already allows the requested data.
4. Match department, role, and data layer.
5. Apply a scoped, unexpired explicit grant only when all grant fields are present.
6. Return the minimum necessary data; otherwise deny with the standard reply.

## Data layers

1. `company_shared` / 全公司共用
   - SOP, announcements, product info, public scripts, training docs, general processes.
   - Readable by verified internal members and AI consultants.
2. `department_general` / 部門一般
   - Department workflow, non-sensitive reports, general FAQ, normal task notes.
   - Readable by the same department. AI consultants need an active department assignment for troubleshooting. Cross-department users need an explicit scoped grant.
3. `department_sensitive` / 部門敏感
   - Finance details, HR salary, customer PII, contracts, order details, credentials, medical/beauty records.
   - Readable by executive owner, department lead, or explicitly authorized members only.

## Roles

- `executive_owner`: highest access. Can read all layers and manage permissions.
- `department_lead`: read own department general and own department sensitive when that department authorizes lead access.
- `department_member`: read company shared and own department general.
- `ai_consultant`: read company shared and assigned-department general data for troubleshooting; unassigned department general and department sensitive denied by default.

## Identity authority

- Authoritative: verified Discord numeric user ID and/or OpenClaw sender ID mapped to one person record.
- Informational only: display name, nickname, email address, role label, and plain-text mention.
- A mismatch between authoritative IDs is a deny condition until manually resolved.
- Offboarding or transfer must revoke the old mapping before applying the new one.
- Person status is one of `active`, `pending_id`, or `revoked`; only `active` may proceed to role and data-layer evaluation.

## Explicit grants

An exception is valid only when it records:

- approver ID
- recipient person key
- department and data layer
- reason
- issue time and expiry time

Missing or expired fields mean deny. A grant cannot override source-system permissions.

## Unauthorized reply

這份資料需要主管或資料負責人先同意，我現在不能直接提供。你可以請主管授權，或讓我幫你整理一份不含敏感內容的摘要。

## Personalization vs official writes

Allowed for self:
- tone/style preferences
- persona / agent.soul preferences
- non-sensitive personal memory
- workflow notes

Restricted:
- RLS/security rules
- global config
- credentials/API keys
- other people memories
- official records
- sensitive data in memory
