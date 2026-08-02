from __future__ import annotations

from pathlib import Path

from weekly_ems_news.pipeline import run_draft, run_fetch, run_finalize
from weekly_ems_news.week import iso_week_window


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

    window = iso_week_window(__import__("datetime").date(2026, 8, 2))
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
    assert "Weekly EMS News" in digest
    assert "創傷止血訓練更新" in digest
