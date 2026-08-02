# 02 — 完整分欄編排

**What to build:** Digest 具備完整閱讀骨架：有內容的支柱才出現概覽子彈與分欄；單則為緊湊卡；研究／指引用 PICO、其餘用一般摘要；附錄含產製資訊；空欄不出現「本週無更新」填充句。

**Blocked by:** 01 — 最小可組裝週報（assemble_week 骨架）

**Status:** resolved

- [x] 概覽僅為「目前有條目的支柱」各寫一句子彈
- [x] 臨床／系統／裝備分欄渲染；無料支柱整段省略
- [x] 研究／指引條目以 PICO 四格呈現；其餘為一般摘要
- [x] 附錄含產製資訊（日期區間等）；結構符合 spec 編排
- [x] 上述行為皆有 `assemble_week` fixture 測試覆蓋

## Answer

Layout covered by `layout_week` / `minimal_week` assemble tests.

## Parent

`.scratch/weekly-ems-news/spec.md`

## Comments

- Published after maintainer approval of ticket breakdown.
