# 07 — 跨週去重與重大更新再上

**What to build:** 跨週以 canonical URL 去重，避免同一連結反覆進候選；若標為重大更新或本地跟進，允許再上並留下與前次條目的關聯，讓第二波（例如國際指引後的台灣落地）可以出現。

**Blocked by:** 06 — YAML 來源、抓取 adapter 與種子清單

**Status:** resolved

- [x] 已出現過的 canonical URL 預設不再進入新週候選
- [x] 標示重大更新或本地跟進時可再進入候選
- [x] 再上條目可追溯關聯到先前後次項目
- [x] 以多週 fixture／中繼模擬驗證去重與再上行為

## Parent

`.scratch/weekly-ems-news/spec.md`

## Answer

`data/seen_urls.json` + `filter_duplicates` / `remember_items`; reentry via `allow_reentry` + `update_of`.

## Comments

- Published after maintainer approval of ticket breakdown.
- Can proceed in parallel with 08 once 06 is done.
