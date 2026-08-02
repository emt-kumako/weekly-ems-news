from __future__ import annotations

from pathlib import Path

from weekly_ems_news.candidates import finalize_week, write_candidates
from weekly_ems_news.fixtures import load_week_fixture
from weekly_ems_news.week import iso_week_window

FIXTURES = Path(__file__).parent / "fixtures"


def test_draft_and_finalize_preserves_candidates_and_respects_checkbox(
    tmp_path: Path,
):
    meta, items = load_week_fixture(FIXTURES / "layout_week.json")
    week_dir = tmp_path / "weeks" / meta.week_id
    write_candidates(week_dir, meta, items)

    candidates = (week_dir / "candidates.md").read_text(encoding="utf-8")
    assert "## [x] 創傷止血訓練更新" in candidates

    # Uncheck equipment item.
    updated = candidates.replace(
        "## [x] AED 電極片召回通報",
        "## [ ] AED 電極片召回通報",
    )
    (week_dir / "candidates.md").write_text(updated, encoding="utf-8")

    out = finalize_week(week_dir)
    assert out.exists()
    digest = out.read_text(encoding="utf-8")
    assert "創傷止血訓練更新" in digest
    assert "派遣分級指引修訂" in digest
    assert "AED 電極片召回通報" not in digest
    # Candidates preserved.
    assert (week_dir / "candidates.md").exists()
    assert "## [ ] AED 電極片召回通報" in (
        week_dir / "candidates.md"
    ).read_text(encoding="utf-8")


def test_finalize_respects_manual_order_within_pillar(tmp_path: Path):
    meta, items = load_week_fixture(FIXTURES / "selection_week.json")
    by_id = {i.id: i for i in items}
    # Distinct clinical subtopics so half-cap does not drop the pair.
    clinical = [by_id["c-t1"], by_id["c-m1"]]
    others = [by_id["s1"], by_id["e1"]]
    pack = clinical + others
    week_dir = tmp_path / "weeks" / meta.week_id
    write_candidates(week_dir, meta, pack)

    from weekly_ems_news.candidates import render_candidates_markdown

    # Reverse clinical order in candidates; pillar sections stay 臨床→系統→裝備.
    reordered = list(reversed(clinical)) + others
    (week_dir / "candidates.md").write_text(
        render_candidates_markdown(meta, reordered), encoding="utf-8"
    )
    finalize_week(week_dir)
    digest = (week_dir / "digest.md").read_text(encoding="utf-8")
    first = reordered[0].title
    second = reordered[1].title
    assert digest.find(first) < digest.find(second)


def test_iso_week_window_stable():
    w = iso_week_window(__import__("datetime").date(2026, 8, 2))
    assert w.week_id == "2026-W31"
    assert str(w.date_start) == "2026-07-27"
    assert str(w.date_end) == "2026-08-02"
