# 05 — 候選稿 → 定稿 CLI 與按週打包

**What to build:** 半自動編輯閉環：為一週寫出可勾選、可改稿的候選文件；finalize 依勾選與區塊順序產出 digest，並保留候選作歷程；預設日曆週打包，支援 since/until；手動調序可覆寫自動排序。

**Blocked by:** 03 — 選題上限、均衡與排序；04 — 同主題合併／衝突拆則與未定標示

**Status:** resolved

- [x] 可為指定週次產生單一候選文件，含勾選狀態與可編輯草稿欄位
- [x] Finalize 只納入勾選項目，並尊重候選中的手動順序
- [x] Finalize 後 digest 存在，候選文件仍保留可回溯
- [x] 一週的中繼、候選、定稿落在同一週包裝目錄
- [x] 預設日曆週；可以日期下界／上界覆寫
- [x] 命令列可非互動執行（利於日後排程）

## Parent

`.scratch/weekly-ems-news/spec.md`

## Answer

`draft` / `finalize` CLI + `weeks/<week_id>/` packaging; checkbox + within-pillar order covered by tests.

## Comments

- Published after maintainer approval of ticket breakdown.
