# 01 — 閱讀面響應式契約（桌面／平板／手機）

**What to build:** 閱讀入口與單週 digest 在桌面保持側欄＋正文、在窄螢幕（平板／手機）改為清單上排／單欄可掃；鎖住 viewport 與窄版排版線索。必要時微調現有樣式，並在 `build_reading_surface` fixture 測試中鎖定契約；README 簡短說明可在筆電與手機閱讀。不上完整設計系統、不做瀏覽器自動化。

**Blocked by:** None — can start immediately.

**Status:** resolved

- [x] 桌面寬度下閱讀面為週次清單＋正文並陳，單週正文可讀且無強制橫向捲動的版面契約
- [x] 窄視窗／手機寬度下週次清單改為上方（或同等可掃配置），正文單欄可讀
- [x] 產出 HTML 含適當 mobile viewport；品牌圖與正文線索在窄版契約下仍可觀察
- [x] `build_reading_surface` fixture 測試鎖定上述可觀察行為（含既有預設週／空狀態不被破壞）
- [x] README（或同等）註明閱讀入口適用筆電閱讀與手機掃讀
- [x] 不引入瀏覽器自動化或截圖回歸套件

## Parent

`.scratch/responsive-reading-layout/spec.md`

## Comments

- Published after maintainer approval of 1-ticket plan; new feature dir (not folded into closed digest-reading-surface).
- Polished shared digest + shell CSS (720px stack, overflow/touch targets); contract test `test_responsive_contract_at_build_reading_surface`.
