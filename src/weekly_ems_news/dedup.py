from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from weekly_ems_news.models import NewsItem

SeenStore = dict[str, dict[str, Any]]


def seen_store_path(project_root: Path) -> Path:
    return project_root / "data" / "seen_urls.json"


def load_seen(project_root: Path) -> SeenStore:
    path = seen_store_path(project_root)
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return cast(SeenStore, raw)


def save_seen(project_root: Path, seen: SeenStore) -> None:
    path = seen_store_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(seen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def filter_duplicates(
    items: list[NewsItem],
    project_root: Path,
) -> tuple[list[NewsItem], list[str]]:
    """Drop items whose URL was seen unless allow_reentry is set."""
    seen = load_seen(project_root)
    kept: list[NewsItem] = []
    skipped: list[str] = []
    for item in items:
        key = item.url_key()
        if key in seen and not item.allow_reentry:
            skipped.append(key)
            continue
        if key in seen and item.allow_reentry and not item.update_of:
            prior = seen[key].get("item_id")
            item.update_of = str(prior) if prior is not None else None
            if not item.relationship_note:
                item.relationship_note = f"更新自：{item.update_of}"
        kept.append(item)
    return kept, skipped


def remember_items(
    items: list[NewsItem],
    project_root: Path,
    *,
    week_id: str,
) -> None:
    seen = load_seen(project_root)
    for item in items:
        if not item.selected:
            continue
        seen[item.url_key()] = {
            "item_id": item.id,
            "week_id": week_id,
            "title": item.title,
        }
    save_seen(project_root, seen)
