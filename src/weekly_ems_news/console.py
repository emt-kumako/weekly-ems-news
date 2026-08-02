from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from weekly_ems_news.pipeline import (
    run_draft,
    run_fetch,
    run_finalize,
    run_rebuild_reading_surface,
)
from weekly_ems_news.week import WeekWindow, iso_week_window
from weekly_ems_news.week_package import load_candidates, save_candidates

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787


@dataclass(frozen=True)
class WeekStatus:
    week_id: str
    today_week_id: str
    has_items: bool
    has_candidates: bool
    has_digest: bool
    has_digest_html: bool
    tagline: str
    date_start: str
    date_end: str
    item_count: int
    selected_count: int


@dataclass(frozen=True)
class ConsoleResult:
    ok: bool
    message: str
    data: dict[str, Any] | None = None


def window_for_week_id(week_id: str) -> WeekWindow:
    text = week_id.strip()
    match = re.fullmatch(r"(\d{4})-W(\d{2})", text)
    if match:
        year, wnum = int(match.group(1)), int(match.group(2))
        start = date.fromisocalendar(year, wnum, 1)
        end = date.fromisocalendar(year, wnum, 7)
        return WeekWindow(week_id=text, date_start=start, date_end=end)
    base = iso_week_window()
    return WeekWindow(
        week_id=text,
        date_start=base.date_start,
        date_end=base.date_end,
    )


def list_week_ids(project_root: Path) -> list[str]:
    weeks = project_root / "weeks"
    if not weeks.is_dir():
        return []
    names = [p.name for p in weeks.iterdir() if p.is_dir()]
    return sorted(names, reverse=True)


def week_status(
    project_root: Path,
    week_id: str,
    *,
    today: date | None = None,
) -> WeekStatus:
    today_week_id = iso_week_window(today).week_id
    week_dir = project_root / "weeks" / week_id
    has_items = (week_dir / "items.json").is_file()
    has_candidates = (week_dir / "candidates.md").is_file()
    has_digest = (week_dir / "digest.md").is_file()
    has_digest_html = (week_dir / "digest.html").is_file()
    tagline = ""
    date_start = ""
    date_end = ""
    item_count = 0
    selected_count = 0
    if has_items:
        meta, items = load_candidates(week_dir)
        tagline = meta.tagline
        date_start = meta.date_start
        date_end = meta.date_end
        item_count = len(items)
        selected_count = sum(1 for i in items if i.selected)
    return WeekStatus(
        week_id=week_id,
        today_week_id=today_week_id,
        has_items=has_items,
        has_candidates=has_candidates,
        has_digest=has_digest,
        has_digest_html=has_digest_html,
        tagline=tagline,
        date_start=date_start,
        date_end=date_end,
        item_count=item_count,
        selected_count=selected_count,
    )


def candidates_payload(project_root: Path, week_id: str) -> ConsoleResult:
    week_dir = project_root / "weeks" / week_id
    if not (week_dir / "candidates.md").is_file():
        return ConsoleResult(False, f"尚無 candidates.md（請先 draft）：{week_id}")
    meta, items = load_candidates(week_dir)
    return ConsoleResult(
        True,
        f"{len(items)} 則候選",
        {
            "week_id": meta.week_id,
            "tagline": meta.tagline,
            "date_start": meta.date_start,
            "date_end": meta.date_end,
            "items": [
                {
                    "id": i.id,
                    "title": i.title,
                    "source": i.source,
                    "date": i.date,
                    "pillar": i.pillar.value,
                    "why_label": i.why_label.value,
                    "selected": i.selected,
                    "summary": i.summary or "",
                    "url": i.url,
                }
                for i in items
            ],
        },
    )


def save_candidate_selection(
    project_root: Path,
    week_id: str,
    *,
    selected_ids: list[str],
    tagline: str | None = None,
    ordered_ids: list[str] | None = None,
) -> ConsoleResult:
    week_dir = project_root / "weeks" / week_id
    if not (week_dir / "candidates.md").is_file():
        return ConsoleResult(False, f"尚無 candidates.md：{week_id}")
    path = save_candidates(
        week_dir,
        selected_ids=selected_ids,
        tagline=tagline,
        ordered_ids=ordered_ids,
    )
    status = week_status(project_root, week_id)
    return ConsoleResult(
        True,
        f"已儲存選取（{status.selected_count}/{status.item_count}）→ {path.name}",
        {"status": asdict(status)},
    )


def console_fetch(
    project_root: Path,
    week_id: str,
    *,
    offline: bool = False,
) -> ConsoleResult:
    result = run_fetch(
        project_root,
        window_for_week_id(week_id),
        offline=offline,
    )
    return ConsoleResult(
        result.ok,
        result.message,
        {"status": asdict(week_status(project_root, week_id))},
    )


def console_draft(
    project_root: Path,
    week_id: str,
    *,
    fallback: bool = True,
) -> ConsoleResult:
    week_dir = project_root / "weeks" / week_id
    if not (week_dir / "items.json").is_file():
        return ConsoleResult(False, f"尚無 items.json（請先 fetch）：{week_id}")
    result = run_draft(
        project_root,
        week_id=week_id,
        force_fallback=fallback,
    )
    return ConsoleResult(
        result.ok,
        result.message,
        {"status": asdict(week_status(project_root, week_id))},
    )


def console_finalize(project_root: Path, week_id: str) -> ConsoleResult:
    result = run_finalize(project_root, week_id)
    return ConsoleResult(
        result.ok,
        result.message,
        {
            "status": asdict(week_status(project_root, week_id)),
            "reading_path": "reading/index.html",
        },
    )


def console_rebuild(project_root: Path) -> ConsoleResult:
    result = run_rebuild_reading_surface(project_root)
    return ConsoleResult(
        result.ok,
        result.message,
        {"reading_path": "reading/index.html"},
    )


def _console_html() -> str:
    return """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Weekly EMS News｜控制台</title>
<style>
:root {
  --ink: #1c1917;
  --muted: #57534e;
  --line: #e7e5e4;
  --bg: #f5f5f4;
  --paper: #ffffff;
  --accent: #9f1239;
  --ok: #0f766e;
  --bad: #b91c1c;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Iowan Old Style", "Palatino Linotype", Palatino, "Songti TC",
    "Noto Serif TC", Georgia, serif;
  color: var(--ink);
  background:
    radial-gradient(900px 420px at 0% 0%, #fff1f2 0%, transparent 55%),
    var(--bg);
  line-height: 1.55;
}
.wrap { max-width: 48rem; margin: 0 auto; padding: 1.25rem 1rem 3rem; }
header h1 { margin: 0 0 0.25rem; font-size: 1.55rem; }
header p { margin: 0 0 1.25rem; color: var(--muted); }
.panel {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 1rem 1.05rem;
  margin: 0 0 1rem;
}
.panel h2 {
  margin: 0 0 0.75rem;
  font-size: 1.05rem;
  border-bottom: 1px solid var(--line);
  padding-bottom: 0.4rem;
}
.row { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; }
label.field { display: flex; flex-direction: column; gap: 0.25rem; font-size: 0.9rem; }
input[type="text"], textarea {
  font: inherit;
  padding: 0.45rem 0.55rem;
  border: 1px solid var(--line);
  border-radius: 3px;
  min-width: 12rem;
}
textarea { width: 100%; min-height: 3.2rem; }
button, .btn {
  font-family: ui-sans-serif, system-ui, sans-serif;
  font-size: 0.9rem;
  border: 1px solid var(--line);
  background: #fff;
  color: var(--ink);
  border-radius: 3px;
  padding: 0.5rem 0.85rem;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  min-height: 2.5rem;
}
button.primary { background: var(--accent); color: #fff; border-color: var(--accent); }
button:disabled { opacity: 0.5; cursor: wait; }
.checks { font-family: ui-sans-serif, system-ui, sans-serif; font-size: 0.88rem; color: var(--muted); }
.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr));
  gap: 0.5rem;
  margin: 0.75rem 0;
}
.chip {
  border: 1px solid var(--line);
  border-radius: 3px;
  padding: 0.45rem 0.55rem;
  font-family: ui-sans-serif, system-ui, sans-serif;
  font-size: 0.82rem;
}
.chip.on { border-color: #99f6e4; background: #f0fdfa; color: var(--ok); }
.chip.off { color: var(--muted); }
#log {
  white-space: pre-wrap;
  font-family: ui-sans-serif, system-ui, sans-serif;
  font-size: 0.85rem;
  color: var(--muted);
  min-height: 2.5rem;
}
#log.ok { color: var(--ok); }
#log.bad { color: var(--bad); }
.candidate {
  border-top: 1px solid var(--line);
  padding: 0.75rem 0;
}
.candidate:first-child { border-top: 0; }
.candidate label {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.55rem 0.65rem;
  align-items: start;
  cursor: pointer;
}
.candidate .meta { color: var(--muted); font-size: 0.85rem; }
.candidate .sum { margin: 0.2rem 0 0; font-size: 0.92rem; color: var(--muted); }
@media (max-width: 640px) {
  .wrap { padding: 0.85rem; }
  input[type="text"] { min-width: 0; width: 100%; }
}
</style>
</head>
<body>
<main class="wrap">
  <header>
    <h1>Weekly EMS News｜控制台</h1>
    <p>本機操作：抓取 → 草稿 → 勾選 → 定稿 → 閱讀。僅綁定 localhost。</p>
  </header>

  <section class="panel">
    <h2>週次</h2>
    <div class="row">
      <label class="field">週次 id
        <input id="week" type="text" autocomplete="off" />
      </label>
      <button type="button" id="btn-refresh">重新整理狀態</button>
      <a class="btn" id="link-reading" href="/reading/" target="_blank" rel="noopener">打開閱讀面</a>
    </div>
    <p class="checks" id="week-meta"></p>
    <div class="status-grid" id="status-grid"></div>
  </section>

  <section class="panel">
    <h2>流程</h2>
    <div class="row">
      <label class="checks"><input id="offline" type="checkbox" checked /> 離線 fetch（fixture）</label>
      <button type="button" id="btn-fetch">1. Fetch</button>
      <button type="button" id="btn-draft">2. Draft</button>
      <button type="button" id="btn-save" class="primary">儲存勾選</button>
      <button type="button" id="btn-finalize" class="primary">3. Finalize</button>
      <button type="button" id="btn-rebuild">重建閱讀面</button>
    </div>
    <div id="log"></div>
  </section>

  <section class="panel">
    <h2>候選勾選</h2>
    <label class="field">本週標語
      <textarea id="tagline" placeholder="本週標語…"></textarea>
    </label>
    <div id="candidates"></div>
  </section>
</main>
<script>
const $ = (id) => document.getElementById(id);
let busy = false;

function setLog(msg, ok) {
  const el = $("log");
  el.textContent = msg || "";
  el.className = ok === true ? "ok" : ok === false ? "bad" : "";
}

function setBusy(on) {
  busy = on;
  document.querySelectorAll("button").forEach((b) => { b.disabled = on; });
}

async function api(path, opts) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(opts && opts.headers || {}) },
    ...opts,
  });
  const data = await res.json();
  if (!res.ok || data.ok === false) {
    throw new Error(data.message || ("HTTP " + res.status));
  }
  return data;
}

function renderStatus(st) {
  if (!st) return;
  $("week-meta").textContent = (st.date_start && st.date_end)
    ? (st.date_start + " – " + st.date_end + " · 今天所屬週 " + st.today_week_id)
    : ("今天所屬週 " + st.today_week_id);
  const flags = [
    ["items", st.has_items],
    ["candidates", st.has_candidates],
    ["digest.md", st.has_digest],
    ["digest.html", st.has_digest_html],
    ["勾選", st.selected_count + "/" + st.item_count],
  ];
  $("status-grid").innerHTML = flags.map(([k, v]) => {
    if (typeof v === "string") return '<div class="chip">' + k + "：" + v + "</div>";
    return '<div class="chip ' + (v ? "on" : "off") + '">' + k + "：" + (v ? "有" : "無") + "</div>";
  }).join("");
  if (st.tagline) $("tagline").value = st.tagline;
}

function renderCandidates(payload) {
  const box = $("candidates");
  if (!payload || !payload.items) {
    box.innerHTML = '<p class="checks">尚無候選。請先 Fetch → Draft。</p>';
    return;
  }
  $("tagline").value = payload.tagline || "";
  box.innerHTML = payload.items.map((it) => {
    return '<div class="candidate"><label>'
      + '<input type="checkbox" data-id="' + it.id + '"' + (it.selected ? " checked" : "") + " />"
      + '<div><strong>' + escapeHtml(it.title) + '</strong>'
      + '<div class="meta">' + escapeHtml(it.date) + " · " + escapeHtml(it.source)
      + " · " + escapeHtml(it.pillar) + " · " + escapeHtml(it.why_label) + "</div>"
      + (it.summary ? '<p class="sum">' + escapeHtml(it.summary) + "</p>" : "")
      + '</div></label></div>';
  }).join("");
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[c]);
}

function selectedIds() {
  return Array.from(document.querySelectorAll("#candidates input[type=checkbox]"))
    .filter((el) => el.checked)
    .map((el) => el.getAttribute("data-id"));
}

function orderedIds() {
  return Array.from(document.querySelectorAll("#candidates input[type=checkbox]"))
    .map((el) => el.getAttribute("data-id"));
}

async function refreshAll() {
  const week = $("week").value.trim();
  const stRes = await api("/api/status?week=" + encodeURIComponent(week));
  renderStatus(stRes.data.status);
  try {
    const cRes = await api("/api/candidates?week=" + encodeURIComponent(week));
    renderCandidates(cRes.data);
  } catch (e) {
    renderCandidates(null);
  }
}

async function run(label, fn) {
  if (busy) return;
  setBusy(true);
  setLog(label + "…");
  try {
    await fn();
    setLog(label + "完成", true);
  } catch (e) {
    setLog(String(e.message || e), false);
  } finally {
    setBusy(false);
  }
}

$("btn-refresh").onclick = () => run("重新整理", refreshAll);
$("btn-fetch").onclick = () => run("Fetch", async () => {
  const body = {
    week: $("week").value.trim(),
    offline: $("offline").checked,
  };
  const res = await api("/api/fetch", { method: "POST", body: JSON.stringify(body) });
  setLog(res.message, true);
  await refreshAll();
});
$("btn-draft").onclick = () => run("Draft", async () => {
  const res = await api("/api/draft", {
    method: "POST",
    body: JSON.stringify({ week: $("week").value.trim(), fallback: true }),
  });
  setLog(res.message, true);
  await refreshAll();
});
$("btn-save").onclick = () => run("儲存勾選", async () => {
  const res = await api("/api/candidates", {
    method: "PUT",
    body: JSON.stringify({
      week: $("week").value.trim(),
      selected_ids: selectedIds(),
      ordered_ids: orderedIds(),
      tagline: $("tagline").value,
    }),
  });
  setLog(res.message, true);
  renderStatus(res.data.status);
});
$("btn-finalize").onclick = () => run("Finalize", async () => {
  await api("/api/candidates", {
    method: "PUT",
    body: JSON.stringify({
      week: $("week").value.trim(),
      selected_ids: selectedIds(),
      ordered_ids: orderedIds(),
      tagline: $("tagline").value,
    }),
  });
  const res = await api("/api/finalize", {
    method: "POST",
    body: JSON.stringify({ week: $("week").value.trim() }),
  });
  setLog(res.message, true);
  await refreshAll();
});
$("btn-rebuild").onclick = () => run("重建閱讀面", async () => {
  const res = await api("/api/rebuild-reading", { method: "POST", body: "{}" });
  setLog(res.message, true);
});

async function boot() {
  const bootRes = await api("/api/boot");
  $("week").value = bootRes.data.default_week;
  await refreshAll();
}
boot().catch((e) => setLog(String(e.message || e), false));
</script>
</body>
</html>
"""


def _json_response(
    handler: BaseHTTPRequestHandler, code: int, payload: dict[str, Any]
) -> None:
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


def _read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length") or "0")
    if length <= 0:
        return {}
    body = handler.rfile.read(length)
    if not body:
        return {}
    data = json.loads(body.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON body must be an object")
    return data


def make_handler(project_root: Path) -> type[BaseHTTPRequestHandler]:
    root = project_root.resolve()

    class ConsoleHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: object) -> None:
            print(f"[console] {self.address_string()} {fmt % args}", file=sys.stderr)

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            path = parsed.path
            if path in ("/", "/index.html"):
                raw = _console_html().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)
                return
            if path == "/api/boot":
                today = iso_week_window().week_id
                _json_response(
                    self,
                    200,
                    {
                        "ok": True,
                        "message": "boot",
                        "data": {
                            "default_week": today,
                            "weeks": list_week_ids(root),
                        },
                    },
                )
                return
            if path == "/api/status":
                qs = parse_qs(parsed.query)
                week = (qs.get("week") or [iso_week_window().week_id])[0]
                st = week_status(root, week)
                _json_response(
                    self,
                    200,
                    {"ok": True, "message": "status", "data": {"status": asdict(st)}},
                )
                return
            if path == "/api/candidates":
                qs = parse_qs(parsed.query)
                week = (qs.get("week") or [""])[0]
                result = candidates_payload(root, week)
                _json_response(
                    self,
                    200 if result.ok else 400,
                    {
                        "ok": result.ok,
                        "message": result.message,
                        "data": result.data,
                    },
                )
                return
            if path.startswith("/reading/") or path == "/reading":
                rel = path[len("/reading") :].lstrip("/") or "index.html"
                return self._serve_file(root / "reading" / rel, "text/html")
            if path.startswith("/assets/"):
                rel = path[len("/assets/") :]
                return self._serve_file(root / "assets" / rel, None)
            if path.startswith("/weeks/"):
                rel = path[len("/weeks/") :]
                ctype = (
                    "text/html"
                    if rel.endswith(".html")
                    else "text/markdown; charset=utf-8"
                    if rel.endswith(".md")
                    else None
                )
                return self._serve_file(root / "weeks" / rel, ctype)
            _json_response(self, 404, {"ok": False, "message": "not found"})

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            try:
                body = _read_json(self)
            except (ValueError, json.JSONDecodeError) as exc:
                _json_response(self, 400, {"ok": False, "message": str(exc)})
                return
            if parsed.path == "/api/fetch":
                week = str(body.get("week") or "")
                result = console_fetch(
                    root, week, offline=bool(body.get("offline", False))
                )
            elif parsed.path == "/api/draft":
                week = str(body.get("week") or "")
                result = console_draft(
                    root, week, fallback=bool(body.get("fallback", True))
                )
            elif parsed.path == "/api/finalize":
                week = str(body.get("week") or "")
                result = console_finalize(root, week)
            elif parsed.path == "/api/rebuild-reading":
                result = console_rebuild(root)
            else:
                _json_response(self, 404, {"ok": False, "message": "not found"})
                return
            _json_response(
                self,
                200 if result.ok else 400,
                {
                    "ok": result.ok,
                    "message": result.message,
                    "data": result.data,
                },
            )

        def do_PUT(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path != "/api/candidates":
                _json_response(self, 404, {"ok": False, "message": "not found"})
                return
            try:
                body = _read_json(self)
            except (ValueError, json.JSONDecodeError) as exc:
                _json_response(self, 400, {"ok": False, "message": str(exc)})
                return
            week = str(body.get("week") or "")
            selected = body.get("selected_ids") or []
            ordered = body.get("ordered_ids")
            if not isinstance(selected, list):
                _json_response(
                    self, 400, {"ok": False, "message": "selected_ids must be a list"}
                )
                return
            tagline = body.get("tagline")
            result = save_candidate_selection(
                root,
                week,
                selected_ids=[str(x) for x in selected],
                tagline=str(tagline) if tagline is not None else None,
                ordered_ids=[str(x) for x in ordered]
                if isinstance(ordered, list)
                else None,
            )
            _json_response(
                self,
                200 if result.ok else 400,
                {
                    "ok": result.ok,
                    "message": result.message,
                    "data": result.data,
                },
            )

        def _serve_file(self, path: Path, content_type: str | None) -> None:
            try:
                resolved = path.resolve()
                if not resolved.is_relative_to(root) or not resolved.is_file():
                    _json_response(self, 404, {"ok": False, "message": "not found"})
                    return
            except OSError:
                _json_response(self, 404, {"ok": False, "message": "not found"})
                return
            data = resolved.read_bytes()
            if content_type is None:
                if resolved.suffix == ".png":
                    content_type = "image/png"
                elif resolved.suffix == ".css":
                    content_type = "text/css"
                else:
                    content_type = "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return ConsoleHandler


def serve_console(
    project_root: Path,
    *,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
) -> None:
    """Block serving the local console on loopback."""
    handler = make_handler(project_root)
    server = ThreadingHTTPServer((host, port), handler)
    print(
        f"Weekly EMS News console: http://{host}:{port}/  (Ctrl+C to stop)",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)
    finally:
        server.server_close()
