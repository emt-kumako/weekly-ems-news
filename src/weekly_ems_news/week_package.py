from __future__ import annotations

import json
import re
from pathlib import Path

from weekly_ems_news.assemble import assemble_week_from_candidates
from weekly_ems_news.codec import dump_items_payload, load_items, meta_to_dict
from weekly_ems_news.models import (
    ClinicalSubtopic,
    NewsItem,
    PICO,
    Pillar,
    WeekMeta,
    WhyLabel,
)
from weekly_ems_news.week import WeekWindow

__all__ = [
    "load_items",
    "write_candidates",
    "finalize",
    "write_items",
    "write_raw_fetch",
    "render_candidates_markdown",
]

ITEM_HEADER_RE = re.compile(
    r"^## \[(?P<checked>[ xX])\] (?P<title>.+?) <!-- id:(?P<id>[^\s]+) -->\s*$"
)


def write_items(week_dir: Path, meta: WeekMeta, items: list[NewsItem]) -> Path:
    week_dir.mkdir(parents=True, exist_ok=True)
    path = week_dir / "items.json"
    path.write_text(dump_items_payload(meta, items), encoding="utf-8")
    return path


def render_candidates_markdown(meta: WeekMeta, items: list[NewsItem]) -> str:
    lines = [
        f"# Candidates｜{meta.week_id}",
        "",
        f"{meta.date_start} – {meta.date_end}",
        "",
        f"> {meta.tagline}",
        "",
        "勾選 `[x]` 表示納入定稿。區塊順序即 finalize 時的手動順序。",
        "",
    ]
    for item in items:
        mark = "x" if item.selected else " "
        lines.append(f"## [{mark}] {item.title} <!-- id:{item.id} -->")
        lines.append("")
        lines.append(f"- url: {item.url}")
        lines.append(f"- source: {item.source}")
        lines.append(f"- date: {item.date}")
        lines.append(f"- pillar: {item.pillar.value}")
        if item.clinical_subtopic:
            lines.append(f"- clinical_subtopic: {item.clinical_subtopic.value}")
        lines.append(f"- why_label: {item.why_label.value}")
        lines.append(f"- groundedness: {item.groundedness}")
        lines.append(f"- unverified: {'true' if item.unverified else 'false'}")
        if item.relationship_note:
            lines.append(f"- relationship_note: {item.relationship_note}")
        if item.related_urls:
            lines.append(f"- related_urls: {' | '.join(item.related_urls)}")
        lines.append("")
        if item.pico:
            lines.append("```pico")
            lines.append(f"P: {item.pico.population}")
            lines.append(f"I: {item.pico.intervention}")
            lines.append(f"C: {item.pico.comparison}")
            lines.append(f"O: {item.pico.outcome}")
            lines.append("```")
            lines.append("")
        else:
            lines.append("```summary")
            lines.append(item.summary or "")
            lines.append("```")
            lines.append("")
        lines.append("```next_move")
        lines.append(item.next_move)
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def write_candidates(
    week_dir: Path, meta: WeekMeta, items: list[NewsItem]
) -> Path:
    write_items(week_dir, meta, items)
    path = week_dir / "candidates.md"
    path.write_text(render_candidates_markdown(meta, items), encoding="utf-8")
    return path


def _parse_block_map(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in body.splitlines():
        if line.startswith("- ") and ":" in line:
            key, value = line[2:].split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def _parse_fenced(body: str, name: str) -> str | None:
    pattern = re.compile(rf"```{name}\n(.*?)```", re.DOTALL)
    match = pattern.search(body)
    if not match:
        return None
    return match.group(1).strip("\n")


def _parse_candidates_markdown(
    text: str, fallback_items: list[NewsItem]
) -> list[NewsItem]:
    by_id = {i.id: i for i in fallback_items}
    chunks = re.split(r"(?=^## \[)", text, flags=re.MULTILINE)
    parsed: list[NewsItem] = []
    for chunk in chunks:
        header = chunk.splitlines()[0] if chunk.strip() else ""
        match = ITEM_HEADER_RE.match(header.strip())
        if not match:
            continue
        item_id = match.group("id")
        selected = match.group("checked").lower() == "x"
        base = by_id.get(item_id)
        if base is None:
            continue
        fields = _parse_block_map(chunk)
        summary_raw = _parse_fenced(chunk, "summary")
        next_move = _parse_fenced(chunk, "next_move") or base.next_move
        pico_raw = _parse_fenced(chunk, "pico")
        pico = base.pico
        summary = base.summary
        if pico_raw is not None:
            pico_map: dict[str, str] = {}
            for line in pico_raw.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    pico_map[k.strip().upper()] = v.strip()
            pico = PICO(
                population=pico_map.get("P", ""),
                intervention=pico_map.get("I", ""),
                comparison=pico_map.get("C", ""),
                outcome=pico_map.get("O", ""),
            )
        elif summary_raw is not None:
            summary = summary_raw
            pico = None

        why = fields.get("why_label", base.why_label.value)
        pillar = fields.get("pillar", base.pillar.value)
        related = fields.get("related_urls")
        related_urls = (
            [u.strip() for u in related.split("|") if u.strip()]
            if related
            else list(base.related_urls)
        )
        sub = fields.get("clinical_subtopic")
        parsed.append(
            NewsItem(
                id=item_id,
                title=match.group("title").strip(),
                url=fields.get("url", base.url),
                source=fields.get("source", base.source),
                date=fields.get("date", base.date),
                pillar=Pillar(pillar),
                why_label=WhyLabel(why),
                next_move=next_move,
                summary=summary,
                pico=pico,
                clinical_subtopic=ClinicalSubtopic(sub)
                if sub
                else base.clinical_subtopic,
                unverified=fields.get("unverified", "false").lower() == "true",
                related_urls=related_urls,
                relationship_note=fields.get(
                    "relationship_note", base.relationship_note
                ),
                groundedness=int(fields.get("groundedness", base.groundedness)),
                selected=selected,
            )
        )
    return parsed


def finalize(week_dir: Path) -> Path:
    meta, stored = load_items(week_dir / "items.json")
    candidates_text = (week_dir / "candidates.md").read_text(encoding="utf-8")
    tagline_match = re.search(r"^> (.+)$", candidates_text, re.MULTILINE)
    if tagline_match:
        meta = WeekMeta(
            week_id=meta.week_id,
            date_start=meta.date_start,
            date_end=meta.date_end,
            tagline=tagline_match.group(1).strip(),
            header_rel_path=meta.header_rel_path,
            source_count=meta.source_count,
        )
    items = _parse_candidates_markdown(candidates_text, stored)
    result = assemble_week_from_candidates(items, meta)
    out = week_dir / "digest.md"
    out.write_text(result.digest_markdown, encoding="utf-8")
    write_items(week_dir, meta, items)
    return out


def write_raw_fetch(
    week_dir: Path,
    *,
    window: WeekWindow,
    source_count: int,
    errors: list[str],
    items: list[NewsItem],
) -> Path:
    week_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = week_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    payload = {
        "week_id": window.week_id,
        "date_start": window.date_start.isoformat(),
        "date_end": window.date_end.isoformat(),
        "source_count": source_count,
        "item_count": len(items),
        "errors": errors,
        "items": [
            {
                "id": i.id,
                "title": i.title,
                "url": i.url,
                "source": i.source,
                "date": i.date,
                "summary": i.summary,
            }
            for i in items
        ],
        "meta_shape": meta_to_dict(
            WeekMeta(
                week_id=window.week_id,
                date_start=window.date_start.isoformat(),
                date_end=window.date_end.isoformat(),
                tagline="",
                source_count=source_count,
            )
        ),
    }
    path = raw_dir / "fetch.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path

