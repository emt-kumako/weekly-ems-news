from __future__ import annotations

from pathlib import Path

from weekly_ems_news.assemble import assemble_week, assemble_week_auto
from weekly_ems_news.codec import load_items
from weekly_ems_news.models import ClinicalSubtopic, Pillar
from weekly_ems_news.select import MAX_DIGEST_ITEMS

FIXTURES = Path(__file__).parent / "fixtures"


def test_minimal_digest_has_brand_week_tagline_and_card():
    meta, items = load_items(FIXTURES / "minimal_week.json")
    result = assemble_week_auto(items, meta)

    md = result.digest_markdown
    assert "weekly-ems-news-header.png" in md
    assert "2026-W31" in md
    assert "本週聚焦院前復甦與交接品質。" in md
    assert "[成人 OHCA 高壓氧證據更新](https://example.com/ohca)" in md
    assert "**P** 成人 OHCA" in md
    assert "為何重要（跟上認知）" in md
    assert result.item_ids == ("c1",)


def test_layout_hides_empty_pillars_and_matches_overview():
    meta, items = load_items(FIXTURES / "layout_week.json")
    # Drop equipment to ensure empty pillar omission.
    items = [i for i in items if i.pillar != Pillar.EQUIPMENT]
    result = assemble_week(items, meta)
    md = result.digest_markdown

    assert "## 本週概覽" in md
    assert "**臨床：**" in md
    assert "**系統：**" in md
    assert "**裝備：**" not in md.split("## 附錄")[0]
    assert "## 裝備" not in md.split("## 附錄")[0]
    assert "## 臨床" in md
    assert "## 系統" in md
    assert "### 產製資訊" in md
    assert "定稿則數：2" in md


def test_change_practice_sorts_before_knowledge_within_pillar():
    meta, items = load_items(FIXTURES / "selection_week.json")
    result = assemble_week(items, meta)
    clinical_ids = [
        i
        for i in result.item_ids
        if next(x for x in items if x.id == i).pillar == Pillar.CLINICAL
    ]
    # Among selected clinical, 改做法 items should appear before 跟上認知.
    by_id = {i.id: i for i in items}
    labels = [by_id[i].why_label.value for i in clinical_ids]
    if "改做法" in labels and "跟上認知" in labels:
        assert labels.index("改做法") < labels.index("跟上認知")


def test_max_ten_and_pillar_balance():
    meta, items = load_items(FIXTURES / "selection_week.json")
    result = assemble_week(items, meta)
    assert len(result.item_ids) <= MAX_DIGEST_ITEMS

    by_id = {i.id: i for i in items}
    pillars = {by_id[i].pillar for i in result.item_ids}
    assert Pillar.CLINICAL in pillars
    assert Pillar.SYSTEM in pillars
    assert Pillar.EQUIPMENT in pillars


def test_clinical_subtopic_half_cap():
    meta, items = load_items(FIXTURES / "selection_week.json")
    result = assemble_week(items, meta)
    by_id = {i.id: i for i in items}
    clinical = [
        by_id[i]
        for i in result.item_ids
        if by_id[i].pillar == Pillar.CLINICAL
    ]
    if len(clinical) >= 2:
        from collections import Counter

        counts = Counter(
            i.clinical_subtopic
            for i in clinical
            if i.clinical_subtopic
            and i.clinical_subtopic != ClinicalSubtopic.SPECIAL
        )
        for sub, n in counts.items():
            assert n * 2 <= len(clinical), (sub, n, len(clinical))


def test_merge_same_title_and_keep_splits_and_unverified_appendix():
    meta, items = load_items(FIXTURES / "merge_week.json")
    result = assemble_week(items, meta)
    md = result.digest_markdown

    # Merged ILCOR: one primary, related link present.
    assert md.count("ILCOR 共識更新") >= 1
    assert "https://example.com/ilcor-repost" in md
    # Split items both present.
    assert "https://example.com/ped-a" in md
    assert "https://example.com/ped-b" in md
    assert "拆：" in md
    # Unverified marker + appendix.
    assert "`未定／待驗證`" in md
    assert "### 未定／待驗證" in md
    assert "新氣道裝置預印本" in md


def test_thin_week_does_not_pad_to_ten():
    meta, items = load_items(FIXTURES / "minimal_week.json")
    result = assemble_week(items, meta)
    assert len(result.item_ids) == 1


def test_preserve_order_still_enforces_max_ten_and_balance():
    meta, items = load_items(FIXTURES / "selection_week.json")
    # All selected; candidate order is fixture order.
    result = assemble_week(items, meta, preserve_order=True, apply_selection=True)
    assert len(result.item_ids) <= MAX_DIGEST_ITEMS
    by_id = {i.id: i for i in items}
    pillars = {by_id[i].pillar for i in result.item_ids}
    assert Pillar.CLINICAL in pillars
    assert Pillar.SYSTEM in pillars
    assert Pillar.EQUIPMENT in pillars
