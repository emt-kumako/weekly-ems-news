# 02 — Reading surface：週次清單＋預設當週

**What to build:** 專案級閱讀入口列出已有定稿的週次（新→舊）；開啟時預設當天所屬 ISO 週；該週尚無 digest 則顯示空狀態並仍可改選其他週；切換週次可讀對應 digest HTML。並在此收斂主 seam `build_reading_surface` 的契約測試（凍結 today、多週 fixture）。

**Blocked by:** 01 — 單週 Digest HTML

**Status:** resolved

- [x] 存在可打開的閱讀入口，列出有 digest 的週次（新→舊）
- [x] 開啟時預設選取「today」對應的 ISO 週（與 pipeline 日曆週規則一致）
- [x] 預設週無 digest 時有清楚空狀態，且可改選清單中其他週
- [x] 選中週次會顯示該週 digest 正文；目前選中項可辨識
- [x] 自訂／補跑週次 id 只要有 digest 也會出現在清單
- [x] `build_reading_surface` fixture 測試涵蓋：清單、預設週／空狀態、品牌與正文線索（無瀏覽器自動化）

## Parent

`.scratch/digest-reading-surface/spec.md`

## Comments

- Published after maintainer approval; includes former ticket-04 seam tests.
- Implemented: `reading_surface.build_reading_surface` → `reading/index.html`; embeds finalized `digest.html` mains; default via `iso_week_window(today)`. Tests in `tests/test_reading_surface.py`.
