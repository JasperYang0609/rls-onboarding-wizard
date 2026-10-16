# Wizard Questions

## Launch parameters

Ask first:
1. 客戶正式名稱是什麼？
2. 專案代號 client_slug 要用什麼？
3. 是否使用安全公版模板 safe_baseline？
4. 已知有哪些部門與主管嗎？

## Overall mapping, 10–15 minutes

Collect a map only; do not configure details yet:
- departments
- department leads, or mark as normal members if no lead
- major data types
- obvious sensitive data

## Department closed-loop

For each department, finish before moving on:
1. 部門名稱？
2. 部門主管是誰？如果沒有主管，是否全部設為一般部門內員工？
3. 初始成員有哪些？
4. 每位成員的 Discord numeric ID / OpenClaw sender_id？Email 與暱稱只作聯絡資訊，不能作為授權依據。Unknown values become `pending_id`.
5. 哪些資料屬於全公司共用？
6. 哪些資料屬於部門一般？
7. 哪些資料屬於部門敏感？
8. 是否有跨部門協作資料？指定主責部門與協作部門摘要/必要欄位。
9. 寫入 matrix 後，列出正向、wrong-role、跨部門、revoked-ID、pending-ID 測試。
10. 若需要臨時授權，確認核准者是否為最高管理層或資料所屬部門主管，並逐一指定來源、資源、必要欄位與有效時間；敏感資料不得使用萬用範圍。

## Permission change checklist

For offboarding, transfer, promotion:
- Confirm person_key + discord_user_id + openclaw_sender_id match.
- Remove old department/role read permissions.
- Mark the old identity mapping as revoked before adding the new mapping.
- Apply new department/role read permissions.
- Test new access works.
- Test old sensitive access no longer works.
- If IDs mismatch, set status `pending_id` and pause sensitive access.
- Revoke all grants whose recipient, approver, department ownership, or required resource scope is no longer valid.
