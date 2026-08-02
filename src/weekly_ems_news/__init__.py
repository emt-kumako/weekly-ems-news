"""Weekly EMS News — assemble Taiwan-focused prehospital digests."""

from weekly_ems_news.assemble import assemble_week
from weekly_ems_news.models import NewsItem, WeekMeta, WeekAssembly

__all__ = ["assemble_week", "NewsItem", "WeekMeta", "WeekAssembly"]

__version__ = "0.1.0"
