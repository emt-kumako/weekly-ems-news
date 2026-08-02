from __future__ import annotations

from weekly_ems_news.models import NewsItem, Pillar, WeekMeta


def render_header(meta: WeekMeta) -> str:
    lines = [
        f"![Weekly EMS News]({meta.header_rel_path})",
        "",
        f"# Weekly EMS News｜{meta.week_id}",
        "",
        f"{meta.date_start} – {meta.date_end}",
        "",
        f"> {meta.tagline}",
        "",
        "",
    ]
    return "\n".join(lines)


def render_item_card(item: NewsItem) -> str:
    unverified = " · `未定／待驗證`" if item.unverified else ""
    meta_line = (
        f"{item.date} · {item.source} · {item.pillar.value} · "
        f"{item.why_label.value}{unverified}"
    )
    lines = [
        f"### [{item.title}]({item.url})",
        "",
        meta_line,
        "",
    ]
    if item.pico is not None:
        lines.extend(
            [
                "- **P** " + item.pico.population,
                "- **I** " + item.pico.intervention,
                "- **C** " + item.pico.comparison,
                "- **O** " + item.pico.outcome,
                "",
            ]
        )
    elif item.summary:
        lines.extend([item.summary, ""])

    lines.extend(
        [
            f"**為何重要（{item.why_label.value}）：** {item.next_move}",
            "",
        ]
    )
    if item.relationship_note:
        lines.extend([f"*關係：{item.relationship_note}*", ""])
    if item.related_urls:
        related = "；".join(f"<{u}>" for u in item.related_urls)
        lines.extend([f"相關：{related}", ""])
    return "\n".join(lines)


def render_overview(items_by_pillar: dict[Pillar, list[NewsItem]]) -> str:
    bullets: list[str] = []
    for pillar in (Pillar.CLINICAL, Pillar.SYSTEM, Pillar.EQUIPMENT):
        items = items_by_pillar.get(pillar) or []
        if not items:
            continue
        first = items[0]
        bullets.append(f"- **{pillar.value}：** {first.title}")
    if not bullets:
        return ""
    return "## 本週概覽\n\n" + "\n".join(bullets) + "\n\n"


def render_pillar_sections(items_by_pillar: dict[Pillar, list[NewsItem]]) -> str:
    parts: list[str] = []
    for pillar in (Pillar.CLINICAL, Pillar.SYSTEM, Pillar.EQUIPMENT):
        items = items_by_pillar.get(pillar) or []
        if not items:
            continue
        parts.append(f"## {pillar.value}\n")
        for item in items:
            parts.append(render_item_card(item))
    return "\n".join(parts)


def render_appendix(
    meta: WeekMeta,
    items: list[NewsItem],
) -> str:
    lines = ["## 附錄", ""]

    related_blocks: list[str] = []
    for item in items:
        if item.related_urls:
            links = "；".join(f"<{u}>" for u in item.related_urls)
            related_blocks.append(f"- {item.title}：{links}")
    if related_blocks:
        lines.append("### 相關連結")
        lines.append("")
        lines.extend(related_blocks)
        lines.append("")

    unverified = [i for i in items if i.unverified]
    if unverified:
        lines.append("### 未定／待驗證")
        lines.append("")
        for item in unverified:
            lines.append(f"- [{item.title}]({item.url})")
        lines.append("")

    lines.append("### 產製資訊")
    lines.append("")
    lines.append(f"- 週次：{meta.week_id}")
    lines.append(f"- 日期區間：{meta.date_start} – {meta.date_end}")
    lines.append(f"- 定稿則數：{len(items)}")
    if meta.source_count is not None:
        lines.append(f"- 來源數：{meta.source_count}")
    lines.append("")
    return "\n".join(lines)


def render_digest(
    meta: WeekMeta,
    items: list[NewsItem],
    items_by_pillar: dict[Pillar, list[NewsItem]],
) -> str:
    return (
        render_header(meta)
        + render_overview(items_by_pillar)
        + render_pillar_sections(items_by_pillar)
        + render_appendix(meta, items)
    )
