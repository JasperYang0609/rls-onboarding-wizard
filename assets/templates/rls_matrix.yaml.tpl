schema_version: "1.1"

client:
  name: {{client_name_yaml}}
  slug: {{client_slug_yaml}}
  industry: {{industry_yaml}}
  mode: openclaw_read_rls

scope:
  enforcement: openclaw_read_decision
  database_rls_applied: false
  source_permissions_authoritative: true

identity_rules:
  authoritative_fields: [discord_user_id, openclaw_sender_id]
  display_name_is_authority: false
  unknown_default: deny_all_governed_internal_data
  pending_id_default: deny_all_governed_internal_data
  conflicting_id_default: deny_all_governed_internal_data
  revoked_id_default: deny_all_governed_internal_data

authorization_invariants:
  default_decision: deny
  source_permission_ceiling: true
  cross_department_requires_explicit_grant: true
  minimum_necessary_fields_only: true

grant_rules:
  valid_status: active
  recipient_must_be_active_and_verified: true
  approver_must_be_active_and_verified: true
  issued_at_not_in_future: true
  expires_at_required: true
  expires_after_issued_at: true
  valid_approver_roles: [executive_owner, owning_department_lead]
  required_resource_scope: [source_ids, resource_ids, fields]
  sensitive_scope_wildcards_allowed: false

roles:
  executive_owner:
    label: 最高管理層
    can_read: [company_shared, department_general, department_sensitive]
    can_manage_permissions: true
  department_lead:
    label: 部門主管
    can_read: [company_shared, own_department_general, own_department_sensitive]
  department_member:
    label: 一般成員
    can_read: [company_shared, own_department_general]
  ai_consultant:
    label: AI 顧問
    can_read: [company_shared, assigned_department_general]
    denied_by_default: [unassigned_department_general, department_sensitive]

data_layers:
  company_shared:
    label: 全公司共用
  department_general:
    label: 部門一般
  department_sensitive:
    label: 部門敏感
    unauthorized_reply: "這份資料需要主管或資料負責人先同意，我現在不能直接提供。你可以請主管授權，或讓我幫你整理一份不含敏感內容的摘要。"

# Example person fields:
# - person_key: person-001
#   status: active # active | pending_id | revoked
#   discord_user_id: "DISCORD_NUMERIC_ID"
#   openclaw_sender_id: "OPENCLAW_SENDER_ID"
#   department: operations
#   role: department_member
people: []

# Example department fields:
# - department_key: operations
#   lead_person_keys: [person-002]
#   general_sources: []
#   sensitive_sources: []
departments: []

# Example grant fields:
# - grant_id: grant-001
#   status: active # active | revoked | expired
#   approved_by_person_key: person-002
#   recipient_person_key: person-001
#   department: operations
#   data_layer: department_sensitive
#   resource_scope:
#     source_ids: [notion-operations]
#     resource_ids: [project-alpha]
#     fields: [status, owner, due_date]
#   reason: "Time-bounded task"
#   issued_at: "2026-01-01T00:00:00Z"
#   expires_at: "2026-01-02T00:00:00Z"
explicit_grants: []
permission_change_log: []
