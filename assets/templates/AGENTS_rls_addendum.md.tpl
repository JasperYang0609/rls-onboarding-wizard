# {{client_name}} RLS / 身分辨識規則

- 處理 {{client_name}} 任務時，必須優先依 Discord numeric ID / OpenClaw sender_id 辨識成員。
- 不可只依姓名、暱稱、email 判斷權限。
- 權限判斷以 `records/{{client_slug}}/rls_matrix.yaml` 為主要依據。
- ID 尚未補齊者標記 `pending_id`，不得套用敏感資料權限。
- v1 只處理 OpenClaw 內部資料庫 / 知識庫 / records 的讀取權限。
- 資料層級固定三層：全公司共用、部門一般、部門敏感。
- 無權限時用白話回覆：這份資料需要主管或資料負責人先同意，我現在不能直接提供。
- 個人化設定可調整自己的語氣、風格、非敏感 memory；不可修改 RLS、安全規則、他人記憶或寫入敏感資料。
