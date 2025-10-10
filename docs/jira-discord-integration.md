# Jira × Discord 整合指南

## 專案目標
- **即時通知**：當 Jira 中的議題發生特定事件（如建立、更新、狀態變更）時，自動發送通知到指定的 Discord 頻道。
- **簡化流程**：取代手動複製貼上連結的繁瑣工作，讓團隊成員能即時掌握專案動態。
- **資訊清晰**：提供格式化且包含關鍵資訊（議題標題、狀態、負責人、連結等）的 Discord 通知。

## 系統流程
1. **Jira 事件觸發**：使用者在 Jira 上執行操作，觸發預先設定好的 Automation 規則。
2. **Webhook 請求**：Jira Automation 向部署在 Railway 上的 Discord Bot 發送一個 HTTPS POST 請求。
3. **Bot 驗證與處理**：Bot 驗證請求來源的合法性，解析收到的 JSON 資料，並將其轉換為 Discord Embed 格式。
4. **發送 Discord 通知**：Bot 將格式化後的訊息發送到指定的 Discord 頻道。

## 環境變數設定
為了讓 Bot 正常運作，你需要在 Railway 的服務設定中填寫以下環境變數：

| 變數名稱              | 說明                                     | 範例                               |
| --------------------- | ---------------------------------------- | ---------------------------------- |
| `DISCORD_BOT_TOKEN`   | 你的 Discord Bot Token。                 | `MTA4...`                          |
| `DISCORD_CHANNEL_ID`  | 要接收通知的 Discord 文字頻道 ID。       | `123456789012345678`               |
| `JIRA_WEBHOOK_SECRET` | 用於驗證 Jira 請求的自訂密鑰。           | `a-very-secret-string`             |

**注意**：部署時請使用 Railway 平台提供的密鑰管理機制，不要將敏感資訊寫死在程式碼中。

## Railway 設定
1. **取得公開網址**：在你的 Railway 專案中，為此服務新增一個 **Public Networking**。
   - 選擇 **Generate Domain** 來產生一個免費的 `*.up.railway.app` 網域。
   - 這個網址就是你的服務對外的公開 URL，例如：`https://our-discord-bot-production.up.railway.app`。

2. **組合 Webhook URL**：Jira 需要的 Webhook URL 格式如下：
   `https://<你的 Railway 網址>/webhooks/jira?secret=<你的 JIRA_WEBHOOK_SECRET>`

   例如：`https://our-discord-bot-production.up.railway.app/webhooks/jira?secret=a-very-secret-string`

## Jira Automation 設定步驟
1. 進入你的 Jira 專案，在「專案設定」 > 「自動化」中建立一個新的規則。
2. **選擇觸發條件**：例如 `議題已建立` (Issue Created) 或 `議題狀態已變更` (Issue Transitioned)。
3. **新增動作 (Action)**：選擇 `傳送 Web 要求` (Send web request)。
4. **填寫 Webhook 詳細資訊**：
   - **URL**：貼上你在 Railway 設定步驟中組合好的 **Webhook URL**。
   - **方法 (Method)**：`POST`
   - **標頭 (Headers)**：
     - `Content-Type`: `application/json`
   - **Webhook 本文 (Body)**：選擇 `自訂資料` (Custom data)，並使用 Smart Values 貼上你希望傳送的 JSON 內容。

   **範例 JSON Body**：
   ```json
   {
     "timestamp": "{{now.toIso8601}}",
     "webhookEvent": "jira:issue_created",
     "user": {
       "displayName": "{{initiator.displayName}}"
     },
     "issue": {
       "key": "{{issue.key}}",
       "fields": {
         "summary": "{{issue.summary}}",
         "issuetype": {
           "name": "{{issue.issueType.name}}"
         },
         "priority": {
           "name": "{{issue.priority.name}}"
         },
         "status": {
           "name": "{{issue.status.name}}"
         }
       }
     },
     "changelog": {
       "items": {{changelog.items.json}}
     }
   }
   ```
5. **啟用規則**：儲存並啟用該規則。

## 測試與驗證
- **本地測試**：你可以使用 `curl` 或 Postman 等工具模擬 Jira 發送請求，來測試本地運行的 Bot 是否能成功收到並處理。
- **Jira 測試**：在 Jira 中手動觸發你設定的規則（例如，建立一個新議題），然後到指定的 Discord 頻道查看是否收到了預期的通知。
- **查看日誌**：如果通知未出現，可以到 Railway 查看服務的運行日誌，你先前請我加入的 logging 會顯示收到的請求內容和任何錯誤訊息，這將有助於你排查問題。

### `curl` 測試範例
這個指令模擬 Jira 向你的 Bot 發送一個 Webhook 請求。請將 URL 換成你的服務網址。

```bash
# 將 <YOUR_RAILWAY_URL> 和 <YOUR_SECRET> 換成你自己的設定
curl -X POST \
  "https://<YOUR_RAILWAY_URL>/webhooks/jira?secret=<YOUR_SECRET>" \
  -H "Content-Type: application/json" \
  -d 
'{'
        "issue": {
          "key": "TEST-1",
          "fields": {
            "summary": "這是一個來自 curl 的測試議題",
            "status": { "name": "To Do" }
          }
        },
        "user": { "displayName": "Test User" }
      }'
```

如果一切設定正確，你的 Discord 頻道應該會收到一則關於 "TEST-1" 的通知。