# Jira 自動化 × Discord Bot 整合計畫

## 專案目標
- 讓 Jira Automation 的 `Send web request` 觸發後自動推播至指定 Discord 頻道。
- 建立即時且可追溯的通知流程，以加速團隊掌握需求與異動。
- 維持可維護的 API 介面，便於後續擴充與跨專案重用。

## 系統流程概觀
1. Jira Automation 規則被觸發（例如議題建立、狀態轉換、欄位變更）。
2. Jira 透過 HTTPS POST 呼叫 Discord Bot 提供的 `/jira/notify` API。
3. Bot 端驗證請求、解析載荷並格式化 Discord 訊息。
4. Bot 使用 Discord API 將通知送至目標頻道，並回傳成功狀態給 Jira。

## Bot 端實作重點
- **Webhook 端點**：在現有服務或新建的輕量伺服器上新增 `/jira/notify` POST 路由，接收 JSON 載荷。
- **驗證與安全**：實作 Bearer Token 或自訂簽章檢查，拒絕未授權來源；必要時導入 Jira IP 白名單。
- **訊息格式器**：定義標準化訊息模板（包含議題 Key、摘要、狀態、觸發人、連結等），支援進一步的事件型態分支。
- **錯誤處理與紀錄**：記錄請求與發送結果，針對 Discord API 速率限制實作退避策略，並在失敗時回報 Jira。

## 環境變數設定
- `DISCORD_TOKEN`：Discord Bot Token。
- `DISCORD_JIRA_CHANNEL_ID`：要推播訊息的 Discord 文字頻道 ID（整數）。
- `JIRA_WEBHOOK_TOKEN`：Jira Automation 呼叫時需附帶的 Bearer Token，共享密鑰。
- `JIRA_WEB_SERVER_HOST`（選填，預設 `0.0.0.0`）：Webhook 伺服器綁定位址。
- `JIRA_WEB_SERVER_PORT`（選填，預設 `8080`）：Webhook 伺服器監聽埠號。
- `LOG_LEVEL`（選填，預設 `INFO`）：調整應用程式執行時的日誌層級。

在本機開發時，可將上述設定寫入 `.env` 檔案；部署時請使用平台提供的密鑰管理機制。

## Jira Automation 設定步驟
1. 在專案或全站層級新增規則，選擇適用的觸發條件（例如 Issue Created、Transitioned、Field Value Changed）。
2. 視需要加入條件過濾（限定特定專案類型、狀態或標籤）。
3. 新增「Send web request」動作，設定 Method=POST、URL=`https://<your-domain>/jira/notify`、Headers 加入 `Content-Type: application/json` 與授權標頭，Body 使用 smart values 組成 JSON，如下範例。
```json
{
  "issueKey": "{{issue.key}}",
  "summary": "{{issue.fields.summary}}",
  "status": "{{issue.fields.status.name}}",
  "event": "{{triggerIssueEvent}}",
  "link": "{{issue.url}}",
  "triggeredBy": "{{initiator.displayName}}",
  "timestamp": "{{now}}"
}
```
4. 啟用「Delay execution of subsequent rule actions until we get a response」以便檢視回應內容（必要時）。
5. 在 Audit log 確認測試事件的回應狀態，依需求調整規則或載荷格式。

## 測試與驗證流程
- 本地使用 `curl` 或 Postman 模擬 Jira 載荷，驗證端點與 Discord 推播是否正常。
- 在 Jira 建立暫時性規則進行 QA，確認觸發條件與通知格式符合預期。
- 觀察 Bot 與 Jira 的日誌，確保錯誤處理與重試行為符合設計。

### `curl` 範例（以本機 8080 埠為例）
```bash
curl -X POST \
  http://localhost:8080/jira/notify \
  -H "Authorization: Bearer <JIRA_WEBHOOK_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
        "issueKey": "PROJ-123",
        "summary": "範例議題",
        "status": "In Progress",
        "event": "Issue updated",
        "link": "https://jira.example.com/browse/PROJ-123",
        "triggeredBy": "Alice",
        "timestamp": "{{now}}"
      }'
```

確保 Discord Bot 已登入並具有目標頻道的發言權限，否則通知將無法送達。

## 後續維運建議
- 定期輪替 API Token，並同步更新 Jira Automation 設定。
- 視需求擴充訊息模板（例如加入 SLA、優先權、子任務統計）。
- 將關鍵事件寫入監控或警示系統，以偵測通知失敗。
- 撰寫回歸測試或自動檢查腳本，確保 Bot 端的 Discord 權限與頻道設定保持一致。
