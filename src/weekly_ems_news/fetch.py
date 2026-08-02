from __future__ import annotations

import urllib.error
from dataclasses import dataclass, field
from pathlib import Path

from weekly_ems_news.codec import load_items
from weekly_ems_news.models import NewsItem, Pillar, WhyLabel
from weekly_ems_news.sources import Source, enabled_sources
from weekly_ems_news.transport import RawMaterial, fetch_http, is_fixture_source
from weekly_ems_news.week import WeekWindow


@dataclass
class FetchResult:
    items: list[NewsItem] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    source_count: int = 0


def normalize_raw(
    raw: RawMaterial,
    source: Source,
    *,
    date_str: str,
) -> NewsItem:
    pillar = Pillar(source.pillars[0]) if source.pillars else Pillar.SYSTEM
    groundedness = 8 if source.region == "tw" else 2
    return NewsItem(
        id=f"{source.id}-{abs(hash(raw.url)) % 10_000_000}",
        title=raw.title,
        url=raw.url,
        source=source.name,
        date=date_str,
        pillar=pillar,
        why_label=WhyLabel.UPDATE_KNOWLEDGE,
        next_move="",
        summary=raw.excerpt or "（抓取降級：僅有標題／短摘錄，請補為何重要）",
        groundedness=groundedness,
        selected=True,
    )


def fetch_from_sources(
    project_root: Path,
    window: WeekWindow,
    *,
    sources_path: Path | None = None,
    offline: bool = False,
) -> FetchResult:
    path = sources_path or (project_root / "sources.yaml")
    sources = enabled_sources(path)
    result = FetchResult(source_count=len(sources))
    date_str = window.date_end.isoformat()

    for source in sources:
        if is_fixture_source(source):
            if not source.fixture:
                result.errors.append(f"{source.id}: fixture source missing path")
                continue
            fixture_path = project_root / source.fixture
            try:
                _, items = load_items(fixture_path)
            except (OSError, ValueError, KeyError, TypeError) as exc:
                result.errors.append(f"{source.id}: {exc}")
                continue
            for item in items:
                if not item.date:
                    item.date = date_str
                result.items.append(item)
            continue

        if offline:
            result.errors.append(f"{source.id}: skipped (offline mode)")
            continue

        try:
            raw = fetch_http(source)
            result.items.append(normalize_raw(raw, source, date_str=date_str))
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            result.errors.append(f"{source.id}: {exc}")

    return result
