# 08 — LLM 草稿 adapter 與無金鑰降級

**What to build:** 在已有中繼＋短摘錄的前提下產繁中草稿（摘要或 PICO、為何重要標籤與下一動、本週標語）；有 API 金鑰走 LLM；無金鑰時降級為可審候選（中繼＋摘錄，人補欄位）；草稿可重產且可選保留。

**Blocked by:** 06 — YAML 來源、抓取 adapter 與種子清單

**Status:** resolved

- [x] 有金鑰時可產繁中摘要／PICO、為何重要與標語草稿
- [x] 無金鑰時仍能產出可勾選的候選，不阻塞整週流程
- [x] 降級時人需補齊的欄位清楚可辨
- [x] 草稿可重新生成；可選保留先前草稿快取
- [x] LLM 為 adapter，`assemble_week` 測試不依賴真實 API

## Parent

`.scratch/weekly-ems-news/spec.md`

## Answer

`drafting.py` with OpenAI-compatible optional API; `--fallback` / no-key path marks `（待補）`; caches to `raw/drafts.json`.

## Comments

- Published after maintainer approval of ticket breakdown.
- Blocked by 06 (not only 05) per maintainer-approved suggestion.
- Can proceed in parallel with 07 once 06 is done.
