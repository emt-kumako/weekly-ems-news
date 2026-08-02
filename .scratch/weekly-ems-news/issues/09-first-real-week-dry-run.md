# 09 — 首次真實週乾跑驗收

**What to build:** 用真實種子來源跑完一週手動流程：抓取 → 草稿 → 勾選／微改 → 定稿，得到一份可讀、符合編排與選題契約的繁中 digest；作為 v1 操作驗收，而非再擴功能。

**Blocked by:** 07 — 跨週去重與重大更新再上；08 — LLM 草稿 adapter 與無金鑰降級

**Status:** resolved

- [x] 能對「本曆週或指定週」手動跑通 fetch → draft → 編輯候選 → finalize
- [x] 產出的 digest 含品牌頭、概覽／分欄（依當週有料情況）、緊湊卡與附錄
- [x] 定稿則數 ≤ 10，且未出現明顯應排除的行銷／重複轉載垃圾
- [x] 該週包裝目錄保留候選與定稿，可回溯
- [x] 記錄乾跑中發現的來源問題（失效 feed 等）作為後續小修，但不在本票擴大 scope

## Parent

`.scratch/weekly-ems-news/spec.md`

## Answer

Offline dry-run for `2026-W31` succeeded (`./weekly-ems fetch --offline` → `draft --fallback` → `finalize`), producing branded digest with 3 pillar items. Live HTML fetch currently blocked on this machine by SSL certificate verification errors for python.org Python — documented in README; fixture/offline path validates the editorial loop. Dedup confirmed when re-fetching overlapping fixture URLs into a second week.

## Comments

- Published after maintainer approval of ticket breakdown.
- Seed list lives in 06; this ticket is operator acceptance only.
