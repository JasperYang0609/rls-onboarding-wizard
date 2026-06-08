# RLS Baseline

## v1 Scope

Handle only OpenClaw internal database / knowledge / records read permissions.
Manual reminders only for Discord / Notion / Google permissions.

## Data layers

1. `company_shared` / 全公司共用
   - SOP, announcements, product info, public scripts, training docs, general processes.
   - Readable by all internal members and AI consultants.
2. `department_general` / 部門一般
   - Department workflow, non-sensitive reports, general FAQ, normal task notes.
   - Readable by same department. AI consultant may read for troubleshooting. Cross-department users get summary or need authorization.
3. `department_sensitive` / 部門敏感
   - Finance details, HR salary, customer PII, contracts, order details, credentials, medical/beauty records.
   - Readable by executive owner, department lead, or explicitly authorized members only.

## Roles

- `executive_owner`: highest access. Can read all layers and manage permissions.
- `department_lead`: read own department general and own department sensitive when that department authorizes lead access.
- `department_member`: read company shared and own department general.
- `ai_consultant`: read company shared and department general for troubleshooting; department sensitive denied by default unless explicitly authorized.

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
