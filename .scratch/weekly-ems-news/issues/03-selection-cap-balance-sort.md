# 03 — 選題上限、均衡與排序

**What to build:** 組裝時執行選題契約：定稿最多 10 則；有料時臨床／系統／裝備各至少 1；臨床內復甦／創傷／內科輪流且單一子題不超過該週臨床則數一半；欄內先 `改做法` 再按落地性；淡季寧可少於 10，絕不湊假料。

**Blocked by:** 02 — 完整分欄編排

**Status:** resolved

- [x] 輸入超過 10 則合格條目時，定稿不多於 10 則
- [x] 三柱皆有料時，定稿至少各含 1 則
- [x] 臨床子題半數上限在對應 fixture 下成立
- [x] 欄內排序：`改做法` 優先，其次落地性
- [x] 合格條目不足時產出少於 10 則，不產生填充項
- [x] 行為由 `assemble_week` 測試鎖定

## Answer

Selection logic in `select_for_digest`; covered by `selection_week` tests.

## Parent

`.scratch/weekly-ems-news/spec.md`

## Comments

- Published after maintainer approval of ticket breakdown.
