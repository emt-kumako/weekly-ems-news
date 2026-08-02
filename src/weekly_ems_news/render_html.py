from __future__ import annotations

import html
from weekly_ems_news.models import NewsItem, Pillar, WeekMeta, WhyLabel

_WHY_CLASS = {
    WhyLabel.CHANGE_PRACTICE: "why-change",
    WhyLabel.UPDATE_KNOWLEDGE: "why-know",
    WhyLabel.TEACHING: "why-teach",
}


def _e(text: str) -> str:
    return html.escape(text, quote=True)


def _css() -> str:
    return """
:root {
  --ink: #1c1917;
  --muted: #57534e;
  --line: #e7e5e4;
  --bg: #fafaf9;
  --paper: #ffffff;
  --accent: #9f1239;
  --accent-soft: #fff1f2;
  --system: #0f766e;
  --equip: #a16207;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0;
  font-family: "Iowan Old Style", "Palatino Linotype", Palatino, "Songti TC",
    "Noto Serif TC", Georgia, serif;
  color: var(--ink);
  background:
    radial-gradient(1200px 500px at 10% -10%, #fff1f2 0%, transparent 55%),
    linear-gradient(180deg, #f5f5f4 0%, var(--bg) 40%, #f5f5f4 100%);
  line-height: 1.65;
  font-size: 17px;
  overflow-x: hidden;
}
.wrap {
  max-width: 42rem;
  margin: 0 auto;
  padding: 1.25rem 1.1rem 3rem;
  min-width: 0;
}
.hero {
  margin: 0 0 1.25rem;
  border-radius: 2px;
  overflow: hidden;
  background: #0c1222;
}
.hero img {
  display: block;
  width: 100%;
  height: auto;
  vertical-align: middle;
}
.mast {
  margin-bottom: 1.75rem;
}
.mast h1 {
  font-size: clamp(1.45rem, 4vw, 1.85rem);
  line-height: 1.25;
  margin: 0 0 0.35rem;
  letter-spacing: 0.01em;
}
.mast .dates {
  color: var(--muted);
  font-size: 0.95rem;
  margin: 0 0 0.75rem;
}
.tagline {
  margin: 0;
  padding: 0.85rem 1rem;
  background: var(--paper);
  border-left: 3px solid var(--accent);
  color: var(--ink);
  font-size: 1.02rem;
}
.overview-block { margin: 0 0 1.75rem; }
.overview-title {
  font-size: 1rem;
  margin: 0 0 0.5rem;
  letter-spacing: 0.04em;
}
.overview {
  margin: 0;
  padding: 0;
  list-style: none;
}
.overview li {
  padding: 0.45rem 0;
  border-bottom: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.98rem;
}
.overview strong { color: var(--ink); }
.pillar {
  margin: 0 0 2rem;
}
.pillar h2 {
  font-size: 1.15rem;
  margin: 0 0 0.85rem;
  padding-bottom: 0.35rem;
  border-bottom: 2px solid var(--ink);
  letter-spacing: 0.04em;
}
.card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 1rem 1.05rem 1.1rem;
  margin: 0 0 0.85rem;
}
.card h3 {
  font-size: 1.08rem;
  margin: 0 0 0.4rem;
  line-height: 1.35;
}
.card h3 a {
  color: var(--ink);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  overflow-wrap: anywhere;
  word-break: break-word;
}
.card h3 a:hover { border-bottom-color: var(--accent); color: var(--accent); }
.meta {
  font-family: ui-sans-serif, system-ui, sans-serif;
  font-size: 0.78rem;
  color: var(--muted);
  margin: 0 0 0.65rem;
  letter-spacing: 0.02em;
}
.badge {
  display: inline-block;
  font-size: 0.72rem;
  padding: 0.12rem 0.4rem;
  border-radius: 3px;
  margin-left: 0.25rem;
  background: #fef3c7;
  color: #92400e;
}
.pico {
  margin: 0 0 0.65rem;
  padding-left: 1rem;
  color: var(--muted);
  font-size: 0.95rem;
}
.summary { margin: 0 0 0.65rem; }
.why {
  margin: 0;
  padding: 0.65rem 0.75rem;
  border-radius: 3px;
  background: var(--accent-soft);
  font-size: 0.95rem;
}
.why.why-know { background: #f0fdfa; }
.why.why-teach { background: #eff6ff; }
.why-label {
  font-family: ui-sans-serif, system-ui, sans-serif;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: var(--accent);
  display: block;
  margin-bottom: 0.2rem;
}
.rel, .related {
  margin: 0.55rem 0 0;
  font-size: 0.88rem;
  color: var(--muted);
  overflow-wrap: anywhere;
  word-break: break-word;
}
.related a { overflow-wrap: anywhere; }
.appendix {
  margin-top: 2.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.92rem;
}
.appendix h2 {
  font-size: 1rem;
  color: var(--ink);
  margin: 0 0 0.75rem;
}
.appendix h3 {
  font-size: 0.9rem;
  margin: 1rem 0 0.35rem;
  color: var(--ink);
}
.appendix ul { padding-left: 1.1rem; margin: 0.25rem 0 0.75rem; }
@media (max-width: 720px) {
  body { font-size: 16px; }
  .wrap { padding: 0.85rem 0.85rem 2.5rem; }
  .card { padding: 0.85rem; }
  .mast h1 { font-size: clamp(1.3rem, 5.5vw, 1.65rem); }
  .pico { padding-left: 0.85rem; }
}
@media print {
  body { background: #fff; font-size: 11pt; overflow-x: visible; }
  .card { break-inside: avoid; border-color: #ccc; }
}
""".strip()


def _render_card(item: NewsItem) -> str:
    unverified = (
        '<span class="badge">未定／待驗證</span>' if item.unverified else ""
    )
    why_class = _WHY_CLASS.get(item.why_label, "why-know")
    parts = [
        '<article class="card">',
        f'<h3><a href="{_e(item.url)}">{_e(item.title)}</a></h3>',
        (
            f'<p class="meta">{_e(item.date)} · {_e(item.source)} · '
            f"{_e(item.pillar.value)} · {_e(item.why_label.value)}"
            f"{unverified}</p>"
        ),
    ]
    if item.pico is not None:
        parts.append('<ul class="pico">')
        parts.append(f"<li><strong>P</strong> {_e(item.pico.population)}</li>")
        parts.append(f"<li><strong>I</strong> {_e(item.pico.intervention)}</li>")
        parts.append(f"<li><strong>C</strong> {_e(item.pico.comparison)}</li>")
        parts.append(f"<li><strong>O</strong> {_e(item.pico.outcome)}</li>")
        parts.append("</ul>")
    elif item.summary:
        parts.append(f'<p class="summary">{_e(item.summary)}</p>')

    parts.append(
        f'<p class="why {why_class}">'
        f'<span class="why-label">為何重要 · {_e(item.why_label.value)}</span>'
        f"{_e(item.next_move)}</p>"
    )
    if item.relationship_note:
        parts.append(f'<p class="rel">關係：{_e(item.relationship_note)}</p>')
    if item.related_urls:
        links = "；".join(
            f'<a href="{_e(u)}">{_e(u)}</a>' for u in item.related_urls
        )
        parts.append(f'<p class="related">相關：{links}</p>')
    parts.append("</article>")
    return "\n".join(parts)


def render_digest_html(
    meta: WeekMeta,
    items: list[NewsItem],
    items_by_pillar: dict[Pillar, list[NewsItem]],
) -> str:
    overview_items: list[str] = []
    for pillar in (Pillar.CLINICAL, Pillar.SYSTEM, Pillar.EQUIPMENT):
        pillar_items = items_by_pillar.get(pillar) or []
        if not pillar_items:
            continue
        overview_items.append(
            f"<li><strong>{_e(pillar.value)}：</strong>"
            f"{_e(pillar_items[0].title)}</li>"
        )
    overview_html = (
        '<section class="overview-block">'
        "<h2 class=\"overview-title\">本週概覽</h2>"
        f'<ul class="overview">{"".join(overview_items)}</ul>'
        "</section>"
        if overview_items
        else ""
    )

    pillar_blocks: list[str] = []
    for pillar in (Pillar.CLINICAL, Pillar.SYSTEM, Pillar.EQUIPMENT):
        pillar_items = items_by_pillar.get(pillar) or []
        if not pillar_items:
            continue
        cards = "\n".join(_render_card(i) for i in pillar_items)
        pillar_blocks.append(
            f'<section class="pillar" id="pillar-{_e(pillar.name.lower())}">'
            f"<h2>{_e(pillar.value)}</h2>\n{cards}\n</section>"
        )

    related_lis: list[str] = []
    for item in items:
        if item.related_urls:
            links = "；".join(
                f'<a href="{_e(u)}">{_e(u)}</a>' for u in item.related_urls
            )
            related_lis.append(f"<li>{_e(item.title)}：{links}</li>")
    unverified = [i for i in items if i.unverified]
    unverified_lis = [
        f'<li><a href="{_e(i.url)}">{_e(i.title)}</a></li>' for i in unverified
    ]

    appendix_parts = ['<section class="appendix"><h2>附錄</h2>']
    if related_lis:
        appendix_parts.append("<h3>相關連結</h3>")
        appendix_parts.append(f"<ul>{''.join(related_lis)}</ul>")
    if unverified_lis:
        appendix_parts.append("<h3>未定／待驗證</h3>")
        appendix_parts.append(f"<ul>{''.join(unverified_lis)}</ul>")
    appendix_parts.append("<h3>產製資訊</h3><ul>")
    appendix_parts.append(f"<li>週次：{_e(meta.week_id)}</li>")
    appendix_parts.append(
        f"<li>日期區間：{_e(meta.date_start)} – {_e(meta.date_end)}</li>"
    )
    appendix_parts.append(f"<li>定稿則數：{len(items)}</li>")
    if meta.source_count is not None:
        appendix_parts.append(f"<li>來源數：{meta.source_count}</li>")
    appendix_parts.append("</ul></section>")

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Weekly EMS News｜{_e(meta.week_id)}</title>
<style>
{_css()}
</style>
</head>
<body>
<main class="wrap">
  <div class="hero">
    <img src="{_e(meta.header_rel_path)}" alt="Weekly EMS News" />
  </div>
  <header class="mast">
    <h1>Weekly EMS News｜{_e(meta.week_id)}</h1>
    <p class="dates">{_e(meta.date_start)} – {_e(meta.date_end)}</p>
    <p class="tagline">{_e(meta.tagline)}</p>
  </header>
  {overview_html}
  {"".join(pillar_blocks)}
  {"".join(appendix_parts)}
</main>
</body>
</html>
"""
