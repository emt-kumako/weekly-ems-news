# 01 — 最小可組裝週報（assemble_week 骨架）

**What to build:** 用凍結的 fixture 條目就能組出一份最簡週報：含品牌標題圖、週次／日期、一句標語、至少一則緊湊卡；主 seam `assemble_week` 有自動化測試可跑，專案可安裝並執行組裝。

**Blocked by:** None — can start immediately.

**Status:** resolved

- [x] 存在可呼叫的週報組裝入口，輸入為正規化條目＋週次中繼，輸出為可讀的 digest Markdown
- [x] Digest 頂部呈現品牌標題圖、週次身分與一句標語
- [x] 至少一則緊湊卡含標題連結、摘要、「為何重要」基本欄位
- [x] 以 fixture 驅動的 `assemble_week` 測試通過，無需網路或 LLM
- [x] Python 專案可安裝，組裝流程可在本機重複執行

## Answer

`assemble_week` seam + `weekly-ems assemble --fixture` shipped; minimal fixture test green.

## Parent

`.scratch/weekly-ems-news/spec.md`

## Comments

- Published after maintainer approval of ticket breakdown.
