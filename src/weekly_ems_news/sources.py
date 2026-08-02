from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Source:
    id: str
    name: str
    url: str
    type: str
    region: str
    pillars: tuple[str, ...]
    enabled: bool = True
    fixture: str | None = None


def load_sources(path: Path) -> list[Source]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    sources: list[Source] = []
    for row in raw.get("sources", []):
        sources.append(
            Source(
                id=row["id"],
                name=row["name"],
                url=row["url"],
                type=row.get("type", "html"),
                region=row.get("region", "intl"),
                pillars=tuple(row.get("pillars", [])),
                enabled=bool(row.get("enabled", True)),
                fixture=row.get("fixture"),
            )
        )
    return sources


def enabled_sources(path: Path) -> list[Source]:
    return [s for s in load_sources(path) if s.enabled]
