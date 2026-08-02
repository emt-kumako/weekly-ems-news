# 01 — 單週 Digest HTML

**What to build:** 由已組裝的 digest 內容產出舒適閱讀的單週 HTML：品牌標題圖、週次／日期／標語、有料支柱的概覽、臨床／系統／裝備分欄緊湊卡（含 PICO 或摘要、為何重要、未定標示）、附錄；Markdown digest 仍照寫。可用 fixture 驗證單週 HTML 結構。

**Blocked by:** None — can start immediately.

**Status:** resolved

- [x] Finalize（或同等組裝路徑）能產出可在瀏覽器打開的單週 HTML
- [x] HTML 含品牌標題圖、週次身分、標語與好讀排版（桌面可用、手機可掃）
- [x] 正文反映已組裝條目（概覽／分欄／卡片／附錄線索），不重跑選題規則
- [x] `digest.md` 仍一併寫出
- [x] 有 fixture 測試鎖定單週 HTML 的可觀察結構（無需瀏覽器自動化）

## Parent

`.scratch/digest-reading-surface/spec.md`

## Comments

- Published after maintainer approval (3-ticket plan; former ticket 4 merged into 02).
- Implemented: `render_html.render_digest_html`, `WeekAssembly.digest_html`, finalize writes `digest.html` beside `digest.md`. Tests in `tests/test_digest_html.py`.
