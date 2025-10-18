# Jira Webhook Tester 使用說明

這個測試頁可以用來手動觸發 Railway 上的 Jira Webhook，確認 Discord Bot 的通知流程是否正常。

## 檔案位置

- 測試頁：`docs/jira_webhook_tester.html`

將檔案直接用瀏覽器打開即可（雙擊或拖曳到瀏覽器分頁）。不需要額外的建置或伺服器。

## 操作步驟

1. **填寫 Railway Base URL**
   - 請輸入 Railway 部署的網域，例如 `https://your-app.up.railway.app`。
   - 程式會自動在後面加上 `/webhooks/jira`。

2. **輸入 Webhook Secret（若有）**
   - 與 `.env` 或 Railway 環境變數的 `JIRA_WEBHOOK_SECRET` 一致。
   - 留空則直接打 webhook，不會帶 `secret` query。

3. **挑選事件與基本欄位**
   - `Event Type` 提供常見事件的選單。
   - `Issue Key`、`Summary` 會帶入至預設 payload。

4. **檢視與編輯 JSON Payload**
   - 下方文字框會顯示送出的 JSON，必要時可手動編輯。
   - 若修改了上方欄位，可按 `Rebuild Payload` 重建預設內容。

5. **送出請求**
   - 按 `Send to Railway` 後會送 `POST` 到 `/webhooks/jira?secret=...`。
   - 右下角會顯示 Response 的狀態碼與文字內容。
   - 成功時，記得到 Discord 指定頻道確認是否有收到 Embed。

## 排錯建議

- 先用 `curl` 或 Postman 驗證 webhook 是否可達，再用網頁測試。
- 如果顯示 403，確認 secret 是否正確。
- 若收到 200 但 Discord 沒通知，檢查 bot 是否正在運行、環境變數是否設定。
- `payload` 欄位可貼上真實 Jira Webhook JSON 做重現測試。

## 後續擴充

可依需求新增更多事件範本、payload 欄位或將測試頁部署在內部工具站供團隊使用。也可以搭配瀏覽器的 Network 面板觀察詳細請求資訊。***
