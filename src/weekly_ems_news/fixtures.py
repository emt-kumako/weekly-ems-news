from __future__ import annotations

import json
from pathlib import Path

from weekly_ems_news.models import (
    ClinicalSubtopic,
    NewsItem,
    PICO,
    Pillar,
    WeekMeta,
    WhyLabel,
)


def load_week_fixture(path: Path | str) -> tuple[WeekMeta, list[NewsItem]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    meta_raw = data["meta"]
    meta = WeekMeta(
        week_id=meta_raw["week_id"],
        date_start=meta_raw["date_start"],
        date_end=meta_raw["date_end"],
        tagline=meta_raw["tagline"],
        header_rel_path=meta_raw.get(
            "header_rel_path", "../../assets/weekly-ems-news-header.png"
        ),
        source_count=meta_raw.get("source_count"),
    )
    items: list[NewsItem] = []
    for raw in data["items"]:
        pico = None
        if raw.get("pico"):
            pico = PICO(**raw["pico"])
        sub = raw.get("clinical_subtopic")
        items.append(
            NewsItem(
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
            )
        )
    return meta, items
