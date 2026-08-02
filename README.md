# Weekly EMS News

個人用 EMS（緊急醫療）每週精選週報工具。半自動：抓取 → 草稿 → 勾選定稿。

## 開發

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]" --config-settings editable_mode=compat
# 路徑含空白時，建議用專案根目錄的啟動腳本（已設 PYTHONPATH）
chmod +x ./weekly-ems
pytest
./weekly-ems assemble --fixture tests/fixtures/minimal_week.json
```

### 每週流程

```bash
./weekly-ems fetch --week 2026-W31          # 或加 --offline 只跑 fixture 來源
./weekly-ems draft --week 2026-W31          # 無 API 金鑰自動降級；可加 --fallback
# 編輯 weeks/2026-W31/candidates.md（勾選／改稿）
./weekly-ems finalize --week 2026-W31
```

`finalize` 會寫出該週 `digest.md`、`digest.html`，並更新專案閱讀入口的週次清單。

### 閱讀 HTML

定稿後用瀏覽器打開：

```bash
open reading/index.html
```

路徑：`reading/index.html`（專案根目錄下）。左側為已定稿週次（新→舊），預設選取今天所屬 ISO 週；若當週尚未 finalize，會顯示空狀態，仍可改選其他週。單週檔也可直接開 `weeks/<週次>/digest.md` 或 `digest.html`。

版面為基本響應式：筆電／寬螢幕側欄＋正文；平板與手機改為週次清單在上、正文單欄，方便掃讀（無需另開網站）。

只重建閱讀面（不重新抓取、不重跑 draft）時：

```bash
./weekly-ems rebuild-reading
```

有 `OPENAI_API_KEY` 或 `WEEKLY_EMS_API_KEY` 時，`draft` 會嘗試 LLM 草稿。

若線上 `fetch` 出現 SSL 憑證錯誤（常見於 python.org 安裝的 macOS Python），請先為此 Python 安裝憑證，或暫時用 `--offline` 驗證流程（會走 `sources.yaml` 裡的 fixture 來源）。

規格與票據見 `.scratch/weekly-ems-news/`、`.scratch/digest-reading-surface/`、`.scratch/responsive-reading-layout/`。領域詞彙見 `CONTEXT.md`；架構決策見 `docs/adr/`。

核心 module：`pipeline`（`run_fetch` / `run_draft` / `run_finalize` / `run_rebuild_reading_surface`）、`week_package`、`reading_surface`、`assemble_week_auto` / `assemble_week_from_candidates`；CLI 只做 adapter。
