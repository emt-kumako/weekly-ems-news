# 03 — Finalize／rebuild 接線

**What to build:** 定稿流程自動更新該週 HTML 與閱讀入口的週次清單；版面微調時可不重新抓取、只重建閱讀面；文件說明如何打開閱讀入口。失敗時不留下指向缺失 HTML 的清單狀態。

**Blocked by:** 02 — Reading surface：週次清單＋預設當週

**Status:** resolved

- [x] `run_finalize`（或同等）成功後，該週 HTML 與閱讀入口清單已更新
- [x] Markdown digest 行為不變
- [x] 提供可重建閱讀面的路徑（finalize 內建與／或明確 rebuild），無需 refetch
- [x] README（或同等）說明閱讀入口路徑／打開方式
- [x] Finalize 失敗不會留下指向不存在 HTML 的清單項目

## Parent

`.scratch/digest-reading-surface/spec.md`

## Comments

- Published after maintainer approval of 3-ticket plan.
- `run_finalize` writes week digests first, then `build_reading_surface`. Failures return ok=False without refreshing the index. CLI: `rebuild-reading`. README documents `open reading/index.html`.
