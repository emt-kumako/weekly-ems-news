from __future__ import annotations

from datetime import date
from pathlib import Path

from weekly_ems_news.codec import load_items
from weekly_ems_news.models import WeekMeta
from weekly_ems_news.reading_surface import build_reading_surface
from weekly_ems_news.week_package import finalize, write_candidates

FIXTURES = Path(__file__).parent / "fixtures"


def _meta_with_week(meta: WeekMeta, week_id: str) -> WeekMeta:
    return WeekMeta(
        week_id=week_id,
        date_start=meta.date_start,
        date_end=meta.date_end,
        tagline=meta.tagline,
        header_rel_path=meta.header_rel_path,
        source_count=meta.source_count,
    )


def _finalize_fixture(
    project_root: Path, fixture_name: str, *, week_id: str | None = None
) -> str:
    meta, items = load_items(FIXTURES / fixture_name)
    if week_id is not None:
        meta = _meta_with_week(meta, week_id)
    week_dir = project_root / "weeks" / meta.week_id
    write_candidates(week_dir, meta, items)
    finalize(week_dir)
    return meta.week_id


def test_build_reading_surface_lists_weeks_newest_first(tmp_path: Path):
    _finalize_fixture(tmp_path, "minimal_week.json", week_id="2026-W30")
    _finalize_fixture(tmp_path, "layout_week.json", week_id="2026-W31")
    custom = "2026-W29_2026-07-01_2026-07-10"
    _finalize_fixture(tmp_path, "minimal_week.json", week_id=custom)

    surface = build_reading_surface(
        tmp_path, today=date(2026, 8, 2), write=True
    )

    assert surface.week_ids == ("2026-W31", "2026-W30", custom)
    assert surface.today_week_id == "2026-W31"
    assert surface.selected_week_id == "2026-W31"
    assert surface.index_path.is_file()

    html = surface.index_html
    assert html.index("2026-W31") < html.index("2026-W30") < html.index(custom)
    assert custom in html


def test_default_today_week_selected_with_brand_and_body(tmp_path: Path):
    _finalize_fixture(tmp_path, "layout_week.json", week_id="2026-W31")
    _finalize_fixture(tmp_path, "minimal_week.json", week_id="2026-W30")

    surface = build_reading_surface(
        tmp_path, today=date(2026, 8, 2), write=False
    )
    html = surface.index_html

    assert surface.selected_week_id == "2026-W31"
    assert 'data-week-id="2026-W31" aria-current="page"' in html
    assert 'class="week-link is-current"' in html
    assert "weekly-ems-news-header.png" in html
    assert "../assets/weekly-ems-news-header.png" in html
    assert "創傷止血訓練更新" in html
    assert "本週概覽" in html
    assert "附錄" in html
    assert 'data-week-panel="2026-W31"' in html
    assert "is-active" in html
    assert "本週尚無定稿" in html  # empty markup present
    assert 'data-empty-state' in html
    # Empty state not the active default when today has a digest
    assert 'class="empty-state is-active"' not in html


def test_empty_state_when_today_week_missing(tmp_path: Path):
    _finalize_fixture(tmp_path, "layout_week.json", week_id="2026-W31")

    surface = build_reading_surface(
        tmp_path, today=date(2026, 8, 5), write=False
    )
    html = surface.index_html

    assert surface.today_week_id == "2026-W32"
    assert surface.selected_week_id is None
    assert "2026-W32" in html
    assert 'class="empty-state is-active"' in html
    assert "本週尚無定稿" in html
    assert "2026-W31" in html
    assert "創傷止血訓練更新" in html  # other week still embedded
    assert 'aria-current="page"' not in html


def test_weeks_without_digest_omitted(tmp_path: Path):
    _finalize_fixture(tmp_path, "layout_week.json", week_id="2026-W31")
    orphan = tmp_path / "weeks" / "2026-W28"
    orphan.mkdir(parents=True)
    (orphan / "candidates.md").write_text("# draft only\n", encoding="utf-8")

    surface = build_reading_surface(
        tmp_path, today=date(2026, 8, 2), write=False
    )
    assert surface.week_ids == ("2026-W31",)
    assert "2026-W28" not in surface.index_html


def test_responsive_contract_at_build_reading_surface(tmp_path: Path):
    """Desktop rail + narrow stack cues; viewport; brand/body still present."""
    _finalize_fixture(tmp_path, "layout_week.json", week_id="2026-W31")
    _finalize_fixture(tmp_path, "minimal_week.json", week_id="2026-W30")

    surface = build_reading_surface(
        tmp_path, today=date(2026, 8, 2), write=False
    )
    html = surface.index_html

    assert 'name="viewport" content="width=device-width, initial-scale=1"' in html
    # Desktop: week list rail beside body
    assert "grid-template-columns: minmax(10rem, 14rem) minmax(0, 1fr)" in html
    assert 'class="rail"' in html
    assert "週次清單" in html
    # Narrow: stack to one column; week chips wrap above body
    assert "@media (max-width: 720px)" in html
    narrow = html.split("@media (max-width: 720px)", 1)[1]
    assert "grid-template-columns: 1fr" in narrow
    assert "flex-wrap: wrap" in narrow
    # Digest body stays readable on small screens
    assert "overflow-x: hidden" in html
    assert ".hero img" in html and "width: 100%" in html
    assert "weekly-ems-news-header.png" in html
    assert "創傷止血訓練更新" in html
    assert "本週概覽" in html
    assert 'class="card"' in html
    assert "附錄" in html
    # Default-week / empty-state contract still holds
    assert surface.selected_week_id == "2026-W31"
    assert 'aria-current="page"' in html
    assert 'class="empty-state is-active"' not in html
