from __future__ import annotations

from pathlib import Path

from weekly_ems_news.assemble import assemble_week_auto
from weekly_ems_news.codec import load_items
from weekly_ems_news.week_package import finalize, write_candidates

FIXTURES = Path(__file__).parent / "fixtures"


def test_assemble_html_has_brand_structure_and_cards():
    meta, items = load_items(FIXTURES / "layout_week.json")
    result = assemble_week_auto(items, meta)
    html = result.digest_html

    assert "<!DOCTYPE html>" in html
    assert 'lang="zh-Hant"' in html
    assert "weekly-ems-news-header.png" in html
    assert "Weekly EMS News｜2026-W31" in html
    assert meta.tagline in html
    assert "本週概覽" in html
    assert "創傷止血訓練更新" in html
    assert "派遣分級指引修訂" in html
    assert "AED 電極片召回通報" in html
    assert "為何重要" in html
    assert "附錄" in html
    assert "產製資訊" in html
    assert 'class="wrap"' in html
    assert 'class="card"' in html


def test_pico_and_unverified_appear_in_html():
    meta, items = load_items(FIXTURES / "minimal_week.json")
    result = assemble_week_auto(items, meta)
    html = result.digest_html
    assert "<strong>P</strong>" in html
    assert "成人 OHCA" in html

    meta2, items2 = load_items(FIXTURES / "merge_week.json")
    html2 = assemble_week_auto(items2, meta2).digest_html
    assert "未定／待驗證" in html2


def test_finalize_writes_markdown_and_html(tmp_path: Path):
    meta, items = load_items(FIXTURES / "layout_week.json")
    week_dir = tmp_path / "weeks" / meta.week_id
    write_candidates(week_dir, meta, items)
    finalize(week_dir)

    md = week_dir / "digest.md"
    html_path = week_dir / "digest.html"
    assert md.exists()
    assert html_path.exists()
    html = html_path.read_text(encoding="utf-8")
    assert "創傷止血訓練更新" in html
    assert "創傷止血訓練更新" in md.read_text(encoding="utf-8")
