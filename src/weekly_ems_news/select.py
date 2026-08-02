from __future__ import annotations

from collections import defaultdict

from weekly_ems_news.models import (
    WHY_SORT_RANK,
    ClinicalSubtopic,
    NewsItem,
    Pillar,
)

MAX_DIGEST_ITEMS = 10
PILLAR_ORDER = (Pillar.CLINICAL, Pillar.SYSTEM, Pillar.EQUIPMENT)


def sort_items(items: list[NewsItem]) -> list[NewsItem]:
    return sorted(
        items,
        key=lambda i: (
            WHY_SORT_RANK.get(i.why_label, 99),
            -i.groundedness,
            i.date,
            i.id,
        ),
    )


def _clinical_subtopic_ok(
    chosen_clinical: list[NewsItem],
    candidate: NewsItem,
) -> bool:
    if candidate.pillar != Pillar.CLINICAL:
        return True
    # Special-situation / untagged clinical items do not consume the half-cap
    # budget (conflict pairs and major-update specials must be able to co-exist).
    sub = candidate.clinical_subtopic
    if sub is None or sub == ClinicalSubtopic.SPECIAL:
        return True
    clinical_after = chosen_clinical + [candidate]
    total = len(clinical_after)
    if total <= 1:
        return True
    same = sum(
        1
        for i in clinical_after
        if i.clinical_subtopic == sub
    )
    return same * 2 <= total


def _pick_with_rules(
    pool: list[NewsItem],
    *,
    preserve_input_order: bool,
) -> list[NewsItem]:
    if not pool:
        return []

    by_pillar: dict[Pillar, list[NewsItem]] = defaultdict(list)
    for item in pool:
        by_pillar[item.pillar].append(item)

    chosen: list[NewsItem] = []
    chosen_ids: set[str] = set()
    clinical_chosen: list[NewsItem] = []

    for pillar in PILLAR_ORDER:
        if len(chosen) >= MAX_DIGEST_ITEMS:
            break
        for item in by_pillar.get(pillar, []):
            if item.id in chosen_ids:
                continue
            if not _clinical_subtopic_ok(clinical_chosen, item):
                continue
            chosen.append(item)
            chosen_ids.add(item.id)
            if pillar == Pillar.CLINICAL:
                clinical_chosen.append(item)
            break

    for item in pool:
        if len(chosen) >= MAX_DIGEST_ITEMS:
            break
        if item.id in chosen_ids:
            continue
        if not _clinical_subtopic_ok(clinical_chosen, item):
            continue
        chosen.append(item)
        chosen_ids.add(item.id)
        if item.pillar == Pillar.CLINICAL:
            clinical_chosen.append(item)

    if preserve_input_order:
        chosen_set = {i.id for i in chosen}
        return [i for i in pool if i.id in chosen_set]

    grouped: dict[Pillar, list[NewsItem]] = defaultdict(list)
    for item in chosen:
        grouped[item.pillar].append(item)
    ordered: list[NewsItem] = []
    for pillar in PILLAR_ORDER:
        ordered.extend(sort_items(grouped.get(pillar, [])))
    return ordered


def select_for_digest(items: list[NewsItem]) -> list[NewsItem]:
    """Apply cap, pillar balance, clinical subtopic half-cap, and sort."""
    pool = sort_items([i for i in items if i.selected])
    return _pick_with_rules(pool, preserve_input_order=False)


def select_preserving_order(items: list[NewsItem]) -> list[NewsItem]:
    """Same selection rules, but keep the caller's relative order among survivors."""
    pool = [i for i in items if i.selected]
    return _pick_with_rules(pool, preserve_input_order=True)


def group_by_pillar(items: list[NewsItem]) -> dict[Pillar, list[NewsItem]]:
    grouped: dict[Pillar, list[NewsItem]] = defaultdict(list)
    for item in items:
        grouped[item.pillar].append(item)
    for pillar in grouped:
        grouped[pillar] = sort_items(grouped[pillar])
    return dict(grouped)


def group_by_pillar_preserving_order(
    items: list[NewsItem],
) -> dict[Pillar, list[NewsItem]]:
    grouped: dict[Pillar, list[NewsItem]] = defaultdict(list)
    for item in items:
        grouped[item.pillar].append(item)
    return dict(grouped)
