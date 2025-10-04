# 本機測試指南

本文件說明如何在本機準備自動化測試環境、如何撰寫新的測試、以及如何執行完整測試套件。

## 1. 準備環境
- 安裝 Python 3.10 以上版本（`python --version`）。
- 建立並啟用虛擬環境：
  ```powershell
  python -m venv .venv
  .venv\Scripts\activate
  ```
- 在虛擬環境中安裝執行時相依套件與測試工具鏈：
  ```powershell
  pip install -r requirements.txt
  pip install pytest pytest-asyncio
  ```
- （選擇性）若需要本機環境變數，可將 `.env.example` 複製為 `.env`。撰寫測試時優先使用 `monkeypatch.setenv` 以避免載入真實密鑰。

## 2. 測試目錄結構
- 所有測試皆放在 `tests/` 目錄下。
- `tests/conftest.py` 會調整 `sys.path`，確保像 `import bot` 這類匯入可以直接找到專案模組。
- `pytest` 會自動尋找名稱為 `test_*.py` 的檔案與 `test_*` 的函式。

## 3. 撰寫新測試
1. 建立新檔案（例如 `tests/test_commands.py`），或將測試加入既有檔案。
2. 匯入欲測試的模組或函式。
3. 善用 `pytest` 內建的 fixture，例如 `monkeypatch`、`capsys`，或針對協程使用 `pytest.mark.asyncio`。

範例：
```python
import pytest
import bot

@pytest.mark.asyncio
async def test_ping_command_sends_pong(mocker):
    ctx = mocker.Mock()
    await bot.ping(ctx)
    ctx.send.assert_called_once_with("pong!")
```
注意事項：
- 若測試需要修改環境變數，使用 `monkeypatch.setenv` 或 `monkeypatch.delenv` 確保修改僅限該測試。
- 避免只為了變動環境變數而整個重新載入模組，優先改為針對特定相依項目進行 mock。

## 4. 執行測試
- 在專案根目錄執行全部測試：
  ```powershell
  pytest
  ```
- 於首次失敗即停止：
  ```powershell
  pytest --maxfail=1
  ```
- 只執行符合關鍵字的測試：
  ```powershell
  pytest -k "ping"
  ```
- 顯示測試中的標準輸出：
  ```powershell
  pytest -s
  ```

完成後可使用 `deactivate` 離開虛擬環境。
