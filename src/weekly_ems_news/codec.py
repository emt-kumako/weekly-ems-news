from __future__ import annotations

import json
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


def loads_items_payload(data: JsonDict) -> tuple[WeekMeta, list[NewsItem]]:
    return meta_from_dict(data["meta"]), [item_from_dict(i) for i in data["items"]]


def load_items(path: Path | str) -> tuple[WeekMeta, list[NewsItem]]:
    """Single codec for fixture JSON and week-package items.json."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return loads_items_payload(data)


def dump_items_payload(meta: WeekMeta, items: list[NewsItem]) -> str:
    payload = {"meta": meta_to_dict(meta), "items": [item_to_dict(i) for i in items]}
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
