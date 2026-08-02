from __future__ import annotations

from datetime import date
from pathlib import Path

from weekly_ems_news.codec import load_items
from weekly_ems_news.console import (
    candidates_payload,
    console_draft,
    console_fetch,
    console_finalize,
    save_candidate_selection,
    week_status,
    window_for_week_id,
)
from weekly_ems_news.week_package import write_candidates

FIXTURES = Path(__file__).parent / "fixtures"


def test_window_for_iso_week_id():
    w = window_for_week_id("2026-W31")
    assert w.week_id == "2026-W31"
    assert str(w.date_start) == "2026-07-27"
    assert str(w.date_end) == "2026-08-02"


def test_console_save_selection_and_finalize(tmp_path: Path):
    meta, items = load_items(FIXTURES / "layout_week.json")
    week_dir = tmp_path / "weeks" / meta.week_id
    write_candidates(week_dir, meta, items)

    saved = save_candidate_selection(
        tmp_path,
        meta.week_id,
        selected_ids=["c1", "s1"],
        tagline="控制台測試標語",
    )
    assert saved.ok
    st = week_status(tmp_path, meta.week_id, today=date(2026, 8, 2))
    assert st.has_candidates
    assert st.selected_count == 2
    assert st.tagline == "控制台測試標語"

    payload = candidates_payload(tmp_path, meta.week_id)
    assert payload.ok
    assert payload.data is not None
    by_id = {i["id"]: i for i in payload.data["items"]}
    assert by_id["c1"]["selected"] is True
    assert by_id["e1"]["selected"] is False

    finalized = console_finalize(tmp_path, meta.week_id)
    assert finalized.ok
    digest = (week_dir / "digest.html").read_text(encoding="utf-8")
    assert "創傷止血訓練更新" in digest
    assert "派遣分級指引修訂" in digest
    assert "AED 電極片召回通報" not in digest
    assert "控制台測試標語" in digest
    assert (tmp_path / "reading" / "index.html").is_file()


def test_console_fetch_draft_offline(tmp_path: Path):
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

    week_id = "2026-W31"
    fetched = console_fetch(tmp_path, week_id, offline=True)
    assert fetched.ok
    drafted = console_draft(tmp_path, week_id, fallback=True)
    assert drafted.ok
    st = week_status(tmp_path, week_id, today=date(2026, 8, 2))
    assert st.has_items and st.has_candidates
    assert st.item_count >= 1
