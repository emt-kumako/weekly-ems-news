from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from weekly_ems_news.models import (
    ClinicalSubtopic,
    NewsItem,
    PICO,
    Pillar,
    WeekMeta,
    WhyLabel,
)

ITEM_HEADER_RE = re.compile(
    r"^## \[(?P<checked>[ xX])\] (?P<title>.+?) <!-- id:(?P<id>[^\s]+) -->\s*$"
)

JsonDict = dict[str, Any]


def item_to_dict(item: NewsItem) -> JsonDict:
    data: JsonDict = {
        "id": item.id,
        "title": item.title,
        "url": item.url,
        "source": item.source,
        "date": item.date,
        "pillar": item.pillar.value,
        "why_label": item.why_label.value,
        "next_move": item.next_move,
        "summary": item.summary,
        "unverified": item.unverified,
        "related_urls": item.related_urls,
        "relationship_note": item.relationship_note,
        "groundedness": item.groundedness,
        "selected": item.selected,
        "allow_reentry": item.allow_reentry,
        "update_of": item.update_of,
        "canonical_url": item.canonical_url,
    }
    if item.pico:
        data["pico"] = {
            "population": item.pico.population,
            "intervention": item.pico.intervention,
            "comparison": item.pico.comparison,
            "outcome": item.pico.outcome,
        }
    if item.clinical_subtopic:
        data["clinical_subtopic"] = item.clinical_subtopic.value
    return data


def item_from_dict(raw: JsonDict) -> NewsItem:
    pico = None
    if raw.get("pico"):
        pico = PICO(**raw["pico"])
    sub = raw.get("clinical_subtopic")
    return NewsItem(
        id=raw["id"],
        title=raw["title"],
        url=raw["url"],
        source=raw["source"],
        date=raw["date"],
        pillar=Pillar(raw["pillar"]),
        why_label=WhyLabel(raw["why_label"]),
        next_move=raw["next_move"],
        summary=raw.get("summary"),
        pico=pico,
        clinical_subtopic=ClinicalSubtopic(sub) if sub else None,
        unverified=bool(raw.get("unverified", False)),
        related_urls=list(raw.get("related_urls", [])),
        relationship_note=raw.get("relationship_note"),
        groundedness=int(raw.get("groundedness", 0)),
        selected=bool(raw.get("selected", True)),
        allow_reentry=bool(raw.get("allow_reentry", False)),
        update_of=raw.get("update_of"),
        canonical_url=raw.get("canonical_url"),
    )


def meta_to_dict(meta: WeekMeta) -> JsonDict:
    return {
        "week_id": meta.week_id,
        "date_start": meta.date_start,
        "date_end": meta.date_end,
        "tagline": meta.tagline,
        "header_rel_path": meta.header_rel_path,
        "source_count": meta.source_count,
    }


def meta_from_dict(raw: JsonDict) -> WeekMeta:
    return WeekMeta(
        week_id=raw["week_id"],
        date_start=raw["date_start"],
        date_end=raw["date_end"],
        tagline=raw["tagline"],
        header_rel_path=raw.get(
            "header_rel_path", "../../assets/weekly-ems-news-header.png"
        ),
        source_count=raw.get("source_count"),
    )


def write_items_json(path: Path, meta: WeekMeta, items: list[NewsItem]) -> None:
    payload = {"meta": meta_to_dict(meta), "items": [item_to_dict(i) for i in items]}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_items_json(path: Path) -> tuple[WeekMeta, list[NewsItem]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return meta_from_dict(data["meta"]), [item_from_dict(i) for i in data["items"]]


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


def _parse_block_map(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in body.splitlines():
        if line.startswith("- ") and ":" in line:
            key, value = line[2:].split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def _parse_fenced(body: str, name: str) -> str | None:
    pattern = re.compile(
        rf"```{name}\n(.*?)```",
        re.DOTALL,
    )
    match = pattern.search(body)
    if not match:
        return None
    return match.group(1).strip("\n")


def parse_candidates_markdown(text: str, fallback_items: list[NewsItem]) -> list[NewsItem]:
    """Parse candidates.md; order and checkbox state win; fields overlay fallback by id."""
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


def write_candidates(
    week_dir: Path, meta: WeekMeta, items: list[NewsItem]
) -> Path:
    week_dir.mkdir(parents=True, exist_ok=True)
    write_items_json(week_dir / "items.json", meta, items)
    path = week_dir / "candidates.md"
    path.write_text(render_candidates_markdown(meta, items), encoding="utf-8")
    return path


def finalize_week(week_dir: Path) -> Path:
    meta, stored = read_items_json(week_dir / "items.json")
    candidates_text = (week_dir / "candidates.md").read_text(encoding="utf-8")
    # Prefer tagline edits from candidates header blockquote if present.
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
    items = parse_candidates_markdown(candidates_text, stored)
    from weekly_ems_news.assemble import assemble_week

    result = assemble_week(
        items,
        meta,
        apply_merge=False,
        apply_selection=True,
        preserve_order=True,
    )
    out = week_dir / "digest.md"
    out.write_text(result.digest_markdown, encoding="utf-8")
    # Persist selection state back to items.json for history.
    write_items_json(week_dir / "items.json", meta, items)
    return out
