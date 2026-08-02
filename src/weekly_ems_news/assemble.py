from __future__ import annotations

from weekly_ems_news.merge import merge_same_topic_clusters
from weekly_ems_news.models import NewsItem, WeekAssembly, WeekMeta
from weekly_ems_news.render import render_digest
from weekly_ems_news.select import (
    PILLAR_ORDER,
    group_by_pillar,
    group_by_pillar_preserving_order,
    select_for_digest,
    select_preserving_order,
)


def _assemble(
    items: list[NewsItem],
    meta: WeekMeta,
    *,
    apply_merge: bool,
    preserve_order: bool,
) -> WeekAssembly:
    working = list(items)
    if apply_merge:
        working = merge_same_topic_clusters(working)

    if preserve_order:
        selected = select_preserving_order(working)
        by_pillar = group_by_pillar_preserving_order(selected)
    else:
        selected = select_for_digest(working)
        by_pillar = group_by_pillar(selected)

    flat: list[NewsItem] = []
    for pillar in PILLAR_ORDER:
        flat.extend(by_pillar.get(pillar, []))

    markdown = render_digest(meta, flat, by_pillar)
    return WeekAssembly(
        week_id=meta.week_id,
        digest_markdown=markdown,
        item_ids=tuple(i.id for i in flat),
    )


def assemble_week_auto(items: list[NewsItem], meta: WeekMeta) -> WeekAssembly:
    """Fixture / ranked assembly: merge, select, sort within pillars."""
    return _assemble(items, meta, apply_merge=True, preserve_order=False)


def assemble_week_from_candidates(
    items: list[NewsItem], meta: WeekMeta
) -> WeekAssembly:
    """Candidates finalize path: no re-merge; selection rules; preserve order."""
    return _assemble(items, meta, apply_merge=False, preserve_order=True)


def assemble_week(
    items: list[NewsItem],
    meta: WeekMeta,
    *,
    apply_merge: bool = True,
    apply_selection: bool = True,
    preserve_order: bool = False,
) -> WeekAssembly:
    """Compatibility wrapper — prefer the named entry points."""
    if preserve_order:
        return assemble_week_from_candidates(items, meta)
    if apply_merge and apply_selection:
        return assemble_week_auto(items, meta)
    return _assemble(
        items,
        meta,
        apply_merge=apply_merge,
        preserve_order=False,
    )
