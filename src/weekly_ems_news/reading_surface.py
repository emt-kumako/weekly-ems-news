from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from weekly_ems_news.render_html import _css
from weekly_ems_news.week import iso_week_window

INDEX_REL_PATH = "reading/index.html"
_MAIN_RE = re.compile(
    r"<main\b[^>]*>(?P<body>.*)</main>", re.DOTALL | re.IGNORECASE
)
_HEADER_SRC_RE = re.compile(
    r'src="[^"]*weekly-ems-news-header\.png"', re.IGNORECASE
)


@dataclass(frozen=True)
class ReadingSurface:
    """Project-level reading entry: week list + one week body (or empty state)."""

    index_html: str
    week_ids: tuple[str, ...]
    today_week_id: str
    selected_week_id: str | None
    index_path: Path


def _e(text: str) -> str:
    return html.escape(text, quote=True)


def list_digest_week_ids(project_root: Path) -> list[str]:
    """Week folder names that already have digest.html, newest-first."""
    weeks_root = project_root / "weeks"
    if not weeks_root.is_dir():
        return []
    found = [
        p.name
        for p in weeks_root.iterdir()
        if p.is_dir() and (p / "digest.html").is_file()
    ]
    return sorted(found, reverse=True)


def _extract_main_body(digest_html: str) -> str:
    match = _MAIN_RE.search(digest_html)
    if not match:
        raise ValueError("digest.html has no <main> body to embed")
    body = match.group("body")
    # Paths in per-week HTML are relative to weeks/<id>/; surface lives in reading/.
    body = _HEADER_SRC_RE.sub('src="../assets/weekly-ems-news-header.png"', body)
    body = body.replace("../../assets/", "../assets/")
    return body


def _shell_css() -> str:
    return """
.surface {
  display: grid;
  grid-template-columns: minmax(10rem, 14rem) minmax(0, 1fr);
  gap: 0;
  min-height: 100vh;
  align-items: start;
  overflow-x: hidden;
}
.rail {
  position: sticky;
  top: 0;
  align-self: start;
  max-height: 100vh;
  overflow: auto;
  padding: 1.1rem 0.85rem 2rem;
  border-right: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(6px);
  min-width: 0;
}
.rail-brand {
  font-family: ui-sans-serif, system-ui, sans-serif;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0 0 0.35rem;
}
.rail h1 {
  font-size: 1.05rem;
  margin: 0 0 1rem;
  line-height: 1.3;
}
.week-list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.week-list li { margin: 0 0 0.25rem; }
.week-list a {
  display: flex;
  align-items: center;
  min-height: 2.5rem;
  font-family: ui-sans-serif, system-ui, sans-serif;
  font-size: 0.92rem;
  text-decoration: none;
  color: var(--ink);
  padding: 0.45rem 0.55rem;
  border-radius: 3px;
  border: 1px solid transparent;
}
.week-list a:hover { background: #fff; border-color: var(--line); }
.week-list a.is-current {
  background: var(--accent-soft);
  border-color: #fecdd3;
  color: var(--accent);
  font-weight: 600;
}
.stage { min-width: 0; overflow-x: hidden; }
.week-panel { display: none; }
.week-panel.is-active { display: block; }
.empty-state {
  display: none;
  max-width: 42rem;
  margin: 0 auto;
  padding: 2.5rem 1.1rem 3rem;
}
.empty-state.is-active { display: block; }
.empty-state .panel {
  background: var(--paper);
  border: 1px solid var(--line);
  border-left: 3px solid var(--accent);
  border-radius: 4px;
  padding: 1.25rem 1.2rem;
}
.empty-state h2 {
  margin: 0 0 0.5rem;
  font-size: 1.2rem;
}
.empty-state p {
  margin: 0;
  color: var(--muted);
}
@media (max-width: 720px) {
  .surface {
    grid-template-columns: 1fr;
  }
  .rail {
    position: relative;
    max-height: none;
    border-right: 0;
    border-bottom: 1px solid var(--line);
    padding: 0.85rem 0.85rem 1rem;
  }
  .rail h1 { margin-bottom: 0.65rem; }
  .week-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
  }
  .week-list li { margin: 0; }
  .week-list a {
    min-height: 2.75rem;
    padding: 0.55rem 0.75rem;
  }
  .empty-state {
    padding: 1.25rem 0.85rem 2rem;
  }
}
""".strip()


def _render_index(
    *,
    week_ids: list[str],
    today_week_id: str,
    selected_week_id: str | None,
    panels: dict[str, str],
) -> str:
    list_items: list[str] = []
    for week_id in week_ids:
        current = " is-current" if week_id == selected_week_id else ""
        aria = ' aria-current="page"' if week_id == selected_week_id else ""
        list_items.append(
            "<li>"
            f'<a class="week-link{current}" href="#{_e(week_id)}" '
            f'data-week-id="{_e(week_id)}"{aria}>{_e(week_id)}</a>'
            "</li>"
        )

    panel_blocks: list[str] = []
    for week_id in week_ids:
        active = " is-active" if week_id == selected_week_id else ""
        panel_blocks.append(
            f'<div class="week-panel{active}" data-week-panel="{_e(week_id)}" '
            f'id="week-{_e(week_id)}">'
            f'<main class="wrap">{panels[week_id]}</main>'
            "</div>"
        )

    empty_active = " is-active" if selected_week_id is None else ""
    empty_block = f"""
<div class="empty-state{empty_active}" data-empty-state id="empty-state">
  <div class="panel">
    <h2>本週尚無定稿</h2>
    <p>今天所屬週次 <strong>{_e(today_week_id)}</strong> 還沒有 digest。
    請先 finalize 該週，或從週次清單選擇其他已定稿的週次。</p>
  </div>
</div>
""".strip()

    week_ids_js = ", ".join(json.dumps(w, ensure_ascii=False) for w in week_ids)
    default_js = (
        "null"
        if selected_week_id is None
        else json.dumps(selected_week_id, ensure_ascii=False)
    )

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Weekly EMS News｜閱讀</title>
<style>
{_css()}
{_shell_css()}
</style>
</head>
<body>
<div class="surface">
  <nav class="rail" aria-label="週次清單">
    <p class="rail-brand">Weekly EMS News</p>
    <h1>週次清單</h1>
    <ul class="week-list">
      {"".join(list_items) if list_items else "<li>尚無已定稿週次</li>"}
    </ul>
  </nav>
  <div class="stage">
    {empty_block}
    {"".join(panel_blocks)}
  </div>
</div>
<script>
(function () {{
  var weekIds = [{week_ids_js}];
  var defaultWeek = {default_js};

  function show(weekId) {{
    var links = document.querySelectorAll("[data-week-id]");
    var panels = document.querySelectorAll("[data-week-panel]");
    var empty = document.querySelector("[data-empty-state]");
    var found = weekId && weekIds.indexOf(weekId) !== -1;
    links.forEach(function (a) {{
      var on = found && a.getAttribute("data-week-id") === weekId;
      a.classList.toggle("is-current", on);
      if (on) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    }});
    panels.forEach(function (p) {{
      p.classList.toggle(
        "is-active",
        found && p.getAttribute("data-week-panel") === weekId
      );
    }});
    if (empty) empty.classList.toggle("is-active", !found);
    if (found) {{
      history.replaceState(null, "", "#" + weekId);
      document.title = "Weekly EMS News｜" + weekId;
    }} else {{
      history.replaceState(null, "", "#");
      document.title = "Weekly EMS News｜閱讀";
    }}
  }}

  document.querySelectorAll("[data-week-id]").forEach(function (a) {{
    a.addEventListener("click", function (ev) {{
      ev.preventDefault();
      show(a.getAttribute("data-week-id"));
    }});
  }});

  var fromHash = location.hash ? location.hash.slice(1) : "";
  if (fromHash && weekIds.indexOf(fromHash) !== -1) show(fromHash);
  else if (defaultWeek) show(defaultWeek);
  else show(null);
}})();
</script>
</body>
</html>
"""


def build_reading_surface(
    project_root: Path,
    *,
    today: date | None = None,
    write: bool = True,
) -> ReadingSurface:
    """Build the project reading entry from finalized week digest.html files.

    Default selection is the ISO calendar week containing ``today`` (same rules
    as the pipeline). If that week has no digest, the surface opens on an empty
    state while still listing other weeks.
    """
    project_root = project_root.resolve()
    today_week_id = iso_week_window(today).week_id
    week_ids = list_digest_week_ids(project_root)
    selected = today_week_id if today_week_id in week_ids else None

    panels: dict[str, str] = {}
    for week_id in week_ids:
        digest_path = project_root / "weeks" / week_id / "digest.html"
        panels[week_id] = _extract_main_body(
            digest_path.read_text(encoding="utf-8")
        )

    index_html = _render_index(
        week_ids=week_ids,
        today_week_id=today_week_id,
        selected_week_id=selected,
        panels=panels,
    )
    index_path = project_root / INDEX_REL_PATH
    if write:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(index_html, encoding="utf-8")

    return ReadingSurface(
        index_html=index_html,
        week_ids=tuple(week_ids),
        today_week_id=today_week_id,
        selected_week_id=selected,
        index_path=index_path,
    )
