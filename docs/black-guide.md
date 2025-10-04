# 使用 Black 檢查與修正 Python 程式碼

Black 是一款意在提供一致格式的 Python 原始碼格式化工具。以下文件整理了安裝、設定與日常使用方式，協助你在專案中快速導入並維持乾淨的程式碼風格。

## 1. 安裝方式

### 1.1 使用 pip（虛擬環境）
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install black
```

### 1.2 使用 pipx（全域安裝、互不干擾）
```powershell
pip install --user pipx
pipx ensurepath
pipx install black
```

### 1.3 Poetry 或其他套件管理工具
若專案使用 Poetry，可在 `pyproject.toml` 中加入 black：
```toml
[tool.poetry.group.dev.dependencies]
black = "^24.0"
```
然後執行：
```powershell
poetry install
```

## 2. 快速開始

- **格式化單一檔案**：
  ```powershell
  black path\to\file.py
  ```
- **格式化整個專案**：
  ```powershell
  black .
  ```
- **忽略特定路徑**：
  在專案根目錄建立 `pyproject.toml`，並加入：
  ```toml
  [tool.black]
  extend-exclude = "(migrations|static)"
  ```

## 3. 僅檢查不覆寫檔案

在 CI 或 PR 驗證中，常需確保程式碼已符合 Black 規範而不直接修改檔案，可使用：
```powershell
black --check path\to\code
```
搭配 `--diff` 參數可顯示與預期格式的差異：
```powershell
black --check --diff path\to\code
```
若命令結束代碼為 0 代表檔案已符合；代碼為 1 表示 Black 檢測到未符合格式的檔案。

## 4. 常用參數與設定

Black 的預設選項已涵蓋大多數需求，必要時可在 `pyproject.toml` 自訂：
```toml
[tool.black]
line-length = 100
skip-string-normalization = true
include = "\\.pyi?$"
```

其他常見參數：
- `--preview`：啟用下一版可能採用的預覽行為。
- `--target-version py310`：指定程式碼目標版本，以便 Black 採用對應語法。
- `--color`：在終端顯示彩色 diff。

## 5. 與 Git pre-commit 整合

1. 安裝 `pre-commit`：
   ```powershell
   pip install pre-commit
   ```
2. 在專案根目錄建立 `.pre-commit-config.yaml`：
   ```yaml
   repos:
     - repo: https://github.com/psf/black
       rev: 24.8.0
       hooks:
         - id: black
           language_version: python3.11
   ```
3. 啟用 hook：
   ```powershell
   pre-commit install
   ```
此後，每次執行 `git commit` 時，Black 會自動檢查並修正已 staged 的 Python 檔案。

## 6. 整合 CI/CD 流程

在 GitHub Actions 中，可於工作流程加入以下步驟：
```yaml
- name: Check code style with Black
  run: |
    pip install black
    black --check .
```
若採用其他 CI（GitLab CI、Azure Pipelines），同樣在建置腳本中安裝 Black 並執行 `black --check` 即可。

## 7. IDE / 編輯器整合

- **VS Code**：
  1. 安裝 Microsoft 官方的 Python 擴充套件。
  2. 將 `"python.formatting.provider": "black"` 加入 `settings.json`。
  3. 可設定 `"editor.formatOnSave": true` 讓儲存時自動格式化。
- **PyCharm**：在 *Settings → Tools → External Tools* 加入 Black 命令，或改用內建格式化（2023.2 之後提供整合）。
- **NeoVim/Vim**：安裝 `psf/black` 外掛或在 ALE、null-ls 等工具中註冊 Black formatter。

## 8. 常見問題排查

- **找不到 black 命令**：確認虛擬環境已啟用，或將 pipx 安裝路徑加入 PATH。
- **檔案被大量改動**：Black 會重新排版整個檔案，第一次導入建議先獨立 commit，方便追蹤變更。
- **與既有風格衝突**：若專案已有固定 line length 或引號風格，可透過 `pyproject.toml` 的設定調整。

將 Black 納入開發流程後，團隊可以集中精力在邏輯與功能上，而非格式細節，提升協作效率與程式碼品質。
