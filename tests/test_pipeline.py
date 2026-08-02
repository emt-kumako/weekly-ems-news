from __future__ import annotations

from datetime import date
from pathlib import Path

from weekly_ems_news.codec import load_items
from weekly_ems_news.pipeline import (
    run_draft,
    run_fetch,
    run_finalize,
    run_rebuild_reading_surface,
)
from weekly_ems_news.week import iso_week_window
from weekly_ems_news.week_package import write_candidates


def test_run_fetch_draft_finalize_offline(tmp_path: Path):
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
    fixture_src = (
        Path(__file__).parent / "fixtures" / "layout_week.json"
    ).read_text(encoding="utf-8")
    (tmp_path / "layout_week.json").write_text(fixture_src, encoding="utf-8")

    window = iso_week_window(date(2026, 8, 2))
    fetched = run_fetch(
        tmp_path, window, sources_path=sources, offline=True
    )
    assert fetched.ok
    assert (fetched.week_dir / "items.json").exists()

    drafted = run_draft(
        tmp_path, week_id=window.week_id, force_fallback=True
    )
    assert drafted.ok
    assert (drafted.week_dir / "candidates.md").exists()

    finalized = run_finalize(tmp_path, window.week_id)
    assert finalized.ok
    digest = (finalized.week_dir / "digest.md").read_text(encoding="utf-8")
    html = (finalized.week_dir / "digest.html").read_text(encoding="utf-8")
    assert "Weekly EMS News" in digest
    assert "創傷止血訓練更新" in digest
    assert "創傷止血訓練更新" in html
    assert "weekly-ems-news-header.png" in html

    index = tmp_path / "reading" / "index.html"
    assert index.is_file()
    index_html = index.read_text(encoding="utf-8")
    assert window.week_id in index_html
    assert "創傷止血訓練更新" in index_html
    assert str(index) in finalized.message


def test_rebuild_reading_surface_without_refetch(tmp_path: Path):
    meta, items = load_items(
        Path(__file__).parent / "fixtures" / "layout_week.json"
    )
    week_dir = tmp_path / "weeks" / meta.week_id
    write_candidates(week_dir, meta, items)
    assert run_finalize(tmp_path, meta.week_id).ok

    index = tmp_path / "reading" / "index.html"
    index.write_text("stale", encoding="utf-8")

    rebuilt = run_rebuild_reading_surface(tmp_path, today=date(2026, 8, 2))
    assert rebuilt.ok
    html = index.read_text(encoding="utf-8")
    assert "stale" not in html
    assert meta.week_id in html
    assert "創傷止血訓練更新" in html


def test_failed_finalize_does_not_list_missing_digest(tmp_path: Path):
    meta, items = load_items(
        Path(__file__).parent / "fixtures" / "layout_week.json"
    )
    good_dir = tmp_path / "weeks" / meta.week_id
    write_candidates(good_dir, meta, items)
    assert run_finalize(tmp_path, meta.week_id).ok
    before = (tmp_path / "reading" / "index.html").read_text(encoding="utf-8")

    bad_id = "2026-W99"
    bad_dir = tmp_path / "weeks" / bad_id
    bad_dir.mkdir(parents=True)
    # No candidates.md → finalize fails before writing digest.html
    failed = run_finalize(tmp_path, bad_id)
    assert not failed.ok
    assert not (bad_dir / "digest.html").exists()

    after = (tmp_path / "reading" / "index.html").read_text(encoding="utf-8")
    assert after == before
    assert bad_id not in after
