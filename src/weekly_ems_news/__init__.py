"""Weekly EMS News — assemble Taiwan-focused prehospital digests."""

from weekly_ems_news.assemble import (
    assemble_week,
    assemble_week_auto,
    assemble_week_from_candidates,
)
from weekly_ems_news.models import NewsItem, WeekAssembly, WeekMeta

__all__ = [
    "assemble_week",
    "assemble_week_auto",
    "assemble_week_from_candidates",
    "NewsItem",
    "WeekMeta",
    "WeekAssembly",
]

__version__ = "0.1.0"
