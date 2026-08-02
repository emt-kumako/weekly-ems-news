"""Compatibility re-exports — prefer weekly_ems_news.week_package."""

from weekly_ems_news.codec import load_items as read_items_json
from weekly_ems_news.week_package import (
    finalize as finalize_week,
    render_candidates_markdown,
    write_candidates,
    write_items as write_items_json,
)

__all__ = [
    "read_items_json",
    "write_items_json",
    "write_candidates",
    "finalize_week",
    "render_candidates_markdown",
]
