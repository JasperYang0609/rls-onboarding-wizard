# {{client_name}} OpenClaw RLS 現場 Checklist

## 啟動
- [ ] client_name / client_slug 已確認
- [ ] 已使用 safe_baseline
- [ ] records/{{client_slug}}/ 已建立

## 總盤點
- [ ] 部門清單完成
- [ ] 部門主管或一般成員狀態確認
- [ ] 主要資料類型完成
- [ ] 敏感資料初步標記

## 逐部門閉環
- [ ] 部門名稱與主管確認
- [ ] 初始成員 ID 綁定；未補標 pending_id
- [ ] 姓名、暱稱與 email 未被當成授權依據
- [ ] 資料三層分類完成
- [ ] 讀取權限寫入 matrix
- [ ] 正向測試完成
- [ ] wrong-role 與跨部門反向測試完成
- [ ] revoked-ID 測試完成
- [ ] pending_id 測試完成

## 收尾
- [ ] 權限變更前後核對規則說明完成
- [ ] 臨時授權包含核准者、對象、範圍、原因與到期時間
- [ ] 核准者是有效的最高管理層或資料所屬部門主管
- [ ] 臨時授權精確列出來源、資源與必要欄位；敏感資料沒有萬用範圍
- [ ] revoked、expired、future-dated、inactive-party、wrong-approver 授權負向測試完成
- [ ] 已確認來源平台權限仍是最終上限
- [ ] 手動平台權限提醒完成（Discord / Notion / Google）
