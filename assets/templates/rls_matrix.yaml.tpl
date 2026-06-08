client:
  name: "{{client_name}}"
  slug: "{{client_slug}}"
  industry: "{{industry}}"
  mode: openclaw_read_rls

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
    can_read: [company_shared, department_general_for_troubleshooting]
    denied_by_default: [department_sensitive]

data_layers:
  company_shared:
    label: 全公司共用
  department_general:
    label: 部門一般
  department_sensitive:
    label: 部門敏感
    unauthorized_reply: "這份資料需要主管或資料負責人先同意，我現在不能直接提供。你可以請主管授權，或讓我幫你整理一份不含敏感內容的摘要。"

people: []
departments: []
permission_change_log: []
