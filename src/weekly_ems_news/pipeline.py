from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from weekly_ems_news.codec import load_items
from weekly_ems_news.dedup import filter_duplicates, remember_items
from weekly_ems_news.drafting import draft_items, llm_enabled
from weekly_ems_news.fetch import fetch_from_sources
from weekly_ems_news.models import WeekMeta
from weekly_ems_news.reading_surface import build_reading_surface
from weekly_ems_news.week import WeekWindow, ensure_week_dir
from weekly_ems_news.week_package import (
    finalize as package_finalize,
    write_candidates,
    write_items,
    write_raw_fetch,
)


@dataclass(frozen=True)
class StageResult:
    week_id: str
    week_dir: Path
    message: str
    ok: bool = True


def run_fetch(
    project_root: Path,
    window: WeekWindow,
    *,
    sources_path: Path | None = None,
    offline: bool = False,
) -> StageResult:
    """Orchestrate transport → dedup → week-package write → remember."""
    week_dir = ensure_week_dir(project_root, window.week_id)
    fetched = fetch_from_sources(
        project_root,
        window,
        sources_path=sources_path,
        offline=offline,
    )
    write_raw_fetch(
        week_dir,
        window=window,
        source_count=fetched.source_count,
        errors=fetched.errors,
        items=fetched.items,
    )
    kept, skipped = filter_duplicates(fetched.items, project_root)
    meta = WeekMeta(
        week_id=window.week_id,
        date_start=window.date_start.isoformat(),
        date_end=window.date_end.isoformat(),
        tagline="（待補：本週標語）",
        source_count=fetched.source_count,
    )
    write_items(week_dir, meta, kept)
    for item in kept:
        item.selected = True
    remember_items(kept, project_root, week_id=meta.week_id)

    notes = [
        f"Fetched {len(fetched.items)}; after dedup {len(kept)}",
    ]
    if skipped:
        notes.append(f"Dedup skipped {len(skipped)}")
    if fetched.errors:
        notes.append("Errors: " + "; ".join(fetched.errors))
    ok = bool(kept or fetched.items)
    return StageResult(
        week_id=window.week_id,
        week_dir=week_dir,
        message=" | ".join(notes),
        ok=ok,
    )


def run_draft(
    project_root: Path,
    *,
    week_id: str | None = None,
    fixture: Path | None = None,
    window: WeekWindow | None = None,
    force_fallback: bool = False,
) -> StageResult:
    """Orchestrate drafting module → week_package.write_candidates."""
    if fixture is not None:
        meta, items = load_items(fixture)
        if window is not None:
            meta = WeekMeta(
                week_id=window.week_id,
                date_start=window.date_start.isoformat(),
                date_end=window.date_end.isoformat(),
                tagline=meta.tagline,
                header_rel_path=meta.header_rel_path,
                source_count=meta.source_count,
            )
    else:
        if not week_id:
            raise ValueError("run_draft requires week_id or fixture")
        meta, items = load_items(project_root / "weeks" / week_id / "items.json")

    week_dir = ensure_week_dir(project_root, meta.week_id)
    items, meta = draft_items(
        items,
        meta,
        force_fallback=force_fallback or not llm_enabled(),
        cache_dir=week_dir / "raw",
    )
    path = write_candidates(week_dir, meta, items)
    return StageResult(
        week_id=meta.week_id,
        week_dir=week_dir,
        message=f"Wrote {path}",
        ok=True,
    )


def run_rebuild_reading_surface(
    project_root: Path,
    *,
    today: date | None = None,
) -> StageResult:
    """Rebuild reading/index.html from existing week digest.html files (no fetch)."""
    surface = build_reading_surface(project_root, today=today, write=True)
    return StageResult(
        week_id=surface.selected_week_id or surface.today_week_id,
        week_dir=surface.index_path.parent,
        message=(
            f"Wrote {surface.index_path} "
            f"({len(surface.week_ids)} week(s); "
            f"default {surface.selected_week_id or 'empty'})"
        ),
        ok=True,
    )


def run_finalize(project_root: Path, week_id: str) -> StageResult:
    """Finalize week package, then refresh reading surface (week HTML first)."""
    week_dir = project_root / "weeks" / week_id
    if not (week_dir / "candidates.md").exists():
        return StageResult(
            week_id=week_id,
            week_dir=week_dir,
            message=f"Missing candidates.md in {week_dir}",
            ok=False,
        )
    try:
        out = package_finalize(week_dir)
    except Exception as exc:  # noqa: BLE001 — surface failure without stale index
        return StageResult(
            week_id=week_id,
            week_dir=week_dir,
            message=f"Finalize failed (reading surface unchanged): {exc}",
            ok=False,
        )
    if not (week_dir / "digest.html").is_file():
        return StageResult(
            week_id=week_id,
            week_dir=week_dir,
            message=(
                f"Finalize did not produce digest.html; "
                f"reading surface unchanged (digest.md at {out})"
            ),
            ok=False,
        )
    meta, items = load_items(week_dir / "items.json")
    remember_items(items, project_root, week_id=meta.week_id)
    surface = build_reading_surface(project_root, write=True)
    return StageResult(
        week_id=week_id,
        week_dir=week_dir,
        message=f"Wrote {out}; {surface.index_path}",
        ok=True,
    )
