# 04 — 同主題合併／衝突拆則與未定標示

**What to build:** 同主題預設合併為一則並帶相關連結；結論衝突或「原始來源 vs 本地解讀」可拆成兩則並標明關係；高影響但未定內容強制標示 `未定／待驗證`，卡片與附錄都看得到。

**Blocked by:** 02 — 完整分欄編排

**Status:** resolved

- [x] 同主題轉載／重複敘事預設合併，主連結外可列相關連結
- [x] 衝突或層級不同（原始 vs 本地解讀）可拆則並標示關係
- [x] 未定項在單則卡片上可見標記
- [x] 附錄列出未定／待驗證項
- [x] 行為由 `assemble_week` fixture 測試覆蓋

## Answer

Merge/split/unverified covered by `merge_week` assemble tests.

## Parent

`.scratch/weekly-ems-news/spec.md`

## Comments

- Published after maintainer approval of ticket breakdown.
- Can proceed in parallel with 03.
