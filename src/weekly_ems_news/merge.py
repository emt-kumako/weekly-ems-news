from __future__ import annotations

from weekly_ems_news.models import NewsItem


def merge_same_topic_clusters(items: list[NewsItem]) -> list[NewsItem]:
    """
    Merge republish clusters that share the same title (casefold).

    Items marked with relationship_note starting with ``拆：`` stay separate.
    The highest-groundedness item becomes primary; others become related_urls.
    """
    by_title: dict[str, list[NewsItem]] = {}
    for item in items:
        key = item.title.casefold().strip()
        by_title.setdefault(key, []).append(item)

    result: list[NewsItem] = []
    for group in by_title.values():
        if len(group) == 1:
            result.append(group[0])
            continue

        # Keep separate when any item has an explicit split relationship.
        if any(
            i.relationship_note and i.relationship_note.startswith("拆：")
            for i in group
        ):
            result.extend(group)
            continue

        primary = sorted(group, key=lambda i: (-i.groundedness, i.date, i.id))[0]
        related = []
        for other in group:
            if other.id == primary.id:
                continue
            related.append(other.url)
            related.extend(other.related_urls)
        # Preserve primary related_urls then append others (dedupe, keep order).
        seen: set[str] = set()
        merged_related: list[str] = []
        for url in [*primary.related_urls, *related]:
            if url == primary.url or url in seen:
                continue
            seen.add(url)
            merged_related.append(url)
        primary.related_urls = merged_related
        result.append(primary)
    return result
