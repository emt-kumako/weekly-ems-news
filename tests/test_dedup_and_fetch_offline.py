from __future__ import annotations

from pathlib import Path

from weekly_ems_news.codec import load_items
from weekly_ems_news.dedup import filter_duplicates, remember_items
from weekly_ems_news.drafting import draft_items
from weekly_ems_news.fetch import fetch_from_sources
from weekly_ems_news.models import NewsItem, Pillar, WhyLabel
from weekly_ems_news.week import iso_week_window

FIXTURES = Path(__file__).parent / "fixtures"


def test_offline_fetch_loads_fixture_source(tmp_path: Path):
    # Minimal project root with sources pointing at layout fixture.
    sources = tmp_path / "sources.yaml"
    sources.write_text(
        """
sources:
  - id: offline-demo
    name: Offline
    url: fixture://offline-demo
    type: fixture
    region: tw
    pillars: [臨床]
    enabled: true
    fixture: layout_week.json
""",
        encoding="utf-8",
    )
    (tmp_path / "layout_week.json").write_text(
        (FIXTURES / "layout_week.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    window = iso_week_window(__import__("datetime").date(2026, 8, 2))
    result = fetch_from_sources(
        tmp_path, window, sources_path=sources, offline=True
    )
    assert len(result.items) == 3
    assert not any("skipped" in e and "offline-demo" in e for e in result.errors)


def test_dedup_skips_seen_unless_reentry(tmp_path: Path):
    item = NewsItem(
        id="a1",
        title="同一則",
        url="https://example.com/same",
        source="x",
        date="2026-08-01",
        pillar=Pillar.CLINICAL,
        why_label=WhyLabel.UPDATE_KNOWLEDGE,
        next_move="看一下",
        summary="s",
    )
    remember_items([item], tmp_path, week_id="2026-W30")
    kept, skipped = filter_duplicates([item], tmp_path)
    assert kept == []
    assert skipped == ["https://example.com/same"]

    item.allow_reentry = True
    kept, skipped = filter_duplicates([item], tmp_path)
    assert len(kept) == 1
    assert kept[0].update_of == "a1"


def test_fallback_draft_marks_human_fields():
    meta, items = load_items(FIXTURES / "minimal_week.json")
    items[0].next_move = ""
    drafted, new_meta = draft_items(items, meta, force_fallback=True)
    assert "待補" in drafted[0].next_move
    assert new_meta.tagline
