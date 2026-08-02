# 06 — YAML 來源、抓取 adapter 與種子清單

**What to build:** 以 YAML 維護來源；抓取 adapter 將結果寫成該週中繼資料＋短摘錄（不存全文檔案庫）；內建約 8–12 個官方／學會／期刊／指引種子來源；並提供離線 fixture 路徑，讓不連網也能驗證抓取→組裝接線。

**Blocked by:** 05 — 候選稿 → 定稿 CLI 與按週打包

**Status:** resolved

- [x] 來源清單可在設定中增刪，無需改程式邏輯
- [x] 抓取結果寫入週包裝中的中繼與短摘錄
- [x] 不將全文長期歸檔作為設計目標
- [x] 種子來源約 8–12 個，類型符合 spec（官方／學會／期刊／指引）
- [x] 離線 fixture 可驅動與線上相同的後續 draft／assemble 路徑
- [x] 抓取失敗時有可理解的錯誤／部分成功行為，不默默產空週而無提示

## Parent

`.scratch/weekly-ems-news/spec.md`

## Answer

`sources.yaml` (10 seeds incl. offline fixture) + `fetch` adapter writing `raw/fetch.json` and `items.json`; errors listed on stderr.

## Comments

- Published after maintainer approval of ticket breakdown.
- Seed source list folded into this ticket per maintainer-approved suggestion.
