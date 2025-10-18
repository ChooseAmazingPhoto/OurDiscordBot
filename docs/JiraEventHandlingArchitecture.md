# Jira Webhook 處理架構簡介

## 緣起

隨著 Discord Bot 需要支援愈來愈多 Jira 任務事件（任務建立、狀態轉移、指派變更、到期日調整、評論新增、重開、標籤變更等），舊版僅用條件判斷處理的寫法將難以維護。為了讓新事件可以快速接入，我們把事件處理流程抽象化成「事件註冊 → 類型判斷 → Discord Embed 格式化」三個階段，並提供可插拔的 handler 與 classifier 模式。

## 架構總覽

```
Flask Webhook
      │
      ▼
process_jira_event(data)
      │
      ├─ _determine_event_type(data)
      │       ├─ 直接讀 payload 中的事件欄位
      │       └─ 透過 classifier 細分 jira:issue_updated
      │
      └─ registry.dispatch(event_type, data)
              └─ 導向對應的 handler 模組
```

### 核心元件

- `jira_handler.process_jira_event`：單一入口，負責推論事件類型並呼叫註冊的 handler。
- `jira_events.registry`：保存事件字串與 handler 的對應關係，並自動處理 handler 是否需要 `event_type` 參數。
- `jira_events.classifiers`：管理更新類事件（如 assignee 變更、標籤變動）的判斷函式，以細分 `jira:issue_updated`。
- `jira_events/common.py`：共用工具（時間解析、Issue URL 建立等）。

## 事件模組

每個事件都有獨立模組負責：

| 事件類型 | 模組 | 目前狀態 |
| --- | --- | --- |
| 任務建立 | `jira_events/issue_created.py` | handler 已產出 Embed |
| 狀態轉移 | `jira_events/status_transition.py` | 預留 handler 與 classifier |
| 指派變更 | `jira_events/assignee_changed.py` | 預留 handler 與 classifier |
| 到期日變更 | `jira_events/due_date_changed.py` | 預留 handler 與 classifier |
| 評論新增 | `jira_events/comment_created.py` | 預留 handler |
| 任務重開 | `jira_events/issue_reopened.py` | 預留 handler 與 classifier |
| 標籤變更 | `jira_events/labels_updated.py` | 預留 handler 與 classifier |

在 `jira_events/__init__.py` 會統一呼叫各模組的 `register()`，自動把事件類型與 classifier 掛入系統。

## 擴充流程

1. **建立模組**：在 `jira_events/` 底下新增檔案，提供 `register(registry, register_classifier)` 函式。
2. **註冊事件**：在 `register()` 中呼叫 `registry.register([...], handler)`，必要時註冊 classifier。
3. **實作 handler**：撰寫 `handle_xxx(data, event_type=None)`，回傳 `discord.Embed` 或 `None`。
4. **撰寫 classifier（選擇性）**：若要細分更新事件，實作 `classify_xxx(data)`，判斷 changelog 後回傳事件字串。
5. **註冊模組**：於 `jira_events/__init__.py` 引入新模組並呼叫 `register()`。
6. **新增測試**：在 `tests/test_jira_handler.py` 或專屬測試檔撰寫測試案例。

## 未來工作

- 實作各事件的 classifier 與 handler，讓通知內容更貼近實際需求。
- 規劃 Embed 樣板與統一的樣式（顏色、欄位順序等）。
- 考慮將事件記錄與通知整合到 Bot 指令中，提供查詢或重送功能。

---

若要快速了解現況，請先閱讀 `jira_handler.py` 與 `jira_events/` 內各模組，再依需求補齊對應事件的處理邏輯。這套結構讓新增事件只需聚焦在該事件的解析與呈現，不需重新改動核心路由器。
