from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


@dataclass(frozen=True)
class WeekWindow:
    week_id: str
    date_start: date
    date_end: date

    @property
    def folder_name(self) -> str:
        return self.week_id


def iso_week_window(d: date | None = None) -> WeekWindow:
    d = d or date.today()
    iso = d.isocalendar()
    week_id = f"{iso.year}-W{iso.week:02d}"
    start = date.fromisocalendar(iso.year, iso.week, 1)
    end = date.fromisocalendar(iso.year, iso.week, 7)
    return WeekWindow(week_id=week_id, date_start=start, date_end=end)


def parse_iso_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def window_from_bounds(since: str, until: str) -> WeekWindow:
    start = parse_iso_date(since)
    end = parse_iso_date(until)
    if end < start:
        raise ValueError("until must be on or after since")
    # Label by the ISO week of the start date; custom ranges still pack under that id
    # plus a suffix when range is not a pure ISO week.
    base = iso_week_window(start)
    if start == base.date_start and end == base.date_end:
        return base
    return WeekWindow(
        week_id=f"{base.week_id}_{since}_{until}",
        date_start=start,
        date_end=end,
    )


def resolve_week_dir(project_root: Path, week_id: str) -> Path:
    return project_root / "weeks" / week_id


def ensure_week_dir(project_root: Path, week_id: str) -> Path:
    path = resolve_week_dir(project_root, week_id)
    path.mkdir(parents=True, exist_ok=True)
    return path
