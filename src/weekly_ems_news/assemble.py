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


def assemble_week(
    items: list[NewsItem],
    meta: WeekMeta,
    *,
    apply_merge: bool = True,
    apply_selection: bool = True,
    preserve_order: bool = False,
) -> WeekAssembly:
    """
    Primary seam: normalized items + week meta -> digest markdown.

    When preserve_order is True (finalize from manually ordered candidates),
    selection rules still apply; survivor order follows the candidate order.
    """
    working = list(items)
    if apply_merge:
        working = merge_same_topic_clusters(working)

    if preserve_order:
        selected = (
            select_preserving_order(working)
            if apply_selection
            else [i for i in working if i.selected]
        )
        by_pillar = group_by_pillar_preserving_order(selected)
    elif apply_selection:
        selected = select_for_digest(working)
        by_pillar = group_by_pillar(selected)
    else:
        selected = [i for i in working if i.selected]
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
