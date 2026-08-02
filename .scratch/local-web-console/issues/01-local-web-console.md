# 01 — 本機網頁控制台（完整週流程）

**What to build:** 以 localhost 網頁操作 fetch → draft → 勾選 candidates → finalize → 閱讀面；CLI `serve` 啟動；服務層可測、不重做選題規則。

**Blocked by:** None — can start immediately.

**Status:** resolved

- [x] `serve` 於 127.0.0.1 提供控制台
- [x] 可 fetch／draft／儲存勾選與標語／finalize／rebuild-reading
- [x] finalize 後可開閱讀面
- [x] 服務 seam 有 fixture 測試
- [x] README 說明啟動與 URL

## Parent

`.scratch/local-web-console/spec.md`

## Comments

- Implemented: `console` module + `./weekly-ems serve` → http://127.0.0.1:8787/
