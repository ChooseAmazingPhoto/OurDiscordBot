# Git Commit 規範

本專案採用 Conventional Commits 風格，並強制加入索引鍵 DCBOT。每一次提交都必須遵守以下模板：

`
DCBOT-<ticket>-<type>: <short summary>
`

## 必填內容
- type：從下方允許的前綴中擇一。
- optional-scope：簡短的範圍描述。若不需要則整段（含括號）省略。
- DCBOT-<ticket>：對應工作項目的編號。以實際票號取代 <ticket>，請至branch name取得ticket號碼。
- short summary：50 個字元以內的簡短敘述，使用祈使語氣或片語開頭的小寫句子。

## 可用 type
- feat：新增或調整功能。
- fix：修正錯誤或 Bug。
- docs：僅修改文件。
- style：不影響程式行為的格式或樣式調整。
- refactor：重構；不新增功能也不修 Bug。
- perf：改善效能。
- test：新增或更新測試。
- chore：維運、工具或其他不影響程式行為的變更。
- revert：回復既有提交，必須在內文標示原提交的雜湊值。

## Commit 內文（選填）
- 摘要後空一行，再填寫詳細說明。
- 說明變更動機、影響範圍與測試結果。
- 若有重大相容性變更，另起一段以 BREAKING CHANGE: 開頭並描述影響。

## 分支命名
- 依 Jira 規則使用票證索引鍵建立分支：
  `bash
  git checkout -b DCBOT-<ticket>-<branch-name>
  `
- <branch-name> 以短橫線描述主題。
- 務必使用正確的票證號碼，以便自動化流程與追蹤工具能夠對應。

## 範例
- DCBOT-42-feat:  新增 slash hello 指令
- DCBOT-58-fix:  補上遺漏的 token 檢查
- DCBOT-71-docs:  更新部署流程
- DCBOT-15-revert:  回復舊版 ping 處理

遵循上述規範可維持提交歷史的一致性，並確保發版、變更日誌與票務追蹤自動化流程順利運作。