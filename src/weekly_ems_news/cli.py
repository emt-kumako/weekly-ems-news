from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from weekly_ems_news.assemble import assemble_week
from weekly_ems_news.candidates import (
    finalize_week,
    read_items_json,
    write_candidates,
    write_items_json,
)
from weekly_ems_news.dedup import filter_duplicates, remember_items
from weekly_ems_news.drafting import draft_items, llm_enabled
from weekly_ems_news.fetch import fetch_from_sources, write_fetch_artifacts
from weekly_ems_news.fixtures import load_week_fixture
from weekly_ems_news.models import WeekMeta
from weekly_ems_news.week import (
    WeekWindow,
    ensure_week_dir,
    iso_week_window,
    window_from_bounds,
)


def project_root_from_cwd() -> Path:
    return Path.cwd()


def _window_from_args(args: argparse.Namespace) -> WeekWindow:
    since = getattr(args, "since", None)
    until = getattr(args, "until", None)
    if since and until:
        return window_from_bounds(str(since), str(until))
    week = getattr(args, "week", None)
    if week:
        text = str(week)
        try:
            year_s, w_s = text.split("-W")
            year, wnum = int(year_s), int(w_s)
            start = date.fromisocalendar(year, wnum, 1)
            end = date.fromisocalendar(year, wnum, 7)
            return WeekWindow(
                week_id=f"{year}-W{wnum:02d}",
                date_start=start,
                date_end=end,
            )
        except (ValueError, TypeError):
            base = iso_week_window()
            return WeekWindow(
                week_id=text,
                date_start=base.date_start,
                date_end=base.date_end,
            )
    return iso_week_window()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="weekly-ems")
    sub = parser.add_subparsers(dest="command", required=True)

    assemble_p = sub.add_parser("assemble", help="Assemble digest from JSON fixture")
    assemble_p.add_argument("--fixture", type=Path, required=True)
    assemble_p.add_argument("-o", "--output", type=Path, default=None)

    fetch_p = sub.add_parser(
        "fetch",
        help="Fetch sources into a week package (use --offline for fixture sources only)",
    )
    fetch_p.add_argument("--root", type=Path, default=None)
    fetch_p.add_argument("--week", type=str, default=None)
    fetch_p.add_argument("--since", type=str, default=None)
    fetch_p.add_argument("--until", type=str, default=None)
    fetch_p.add_argument("--offline", action="store_true")
    fetch_p.add_argument(
        "--sources",
        type=Path,
        default=None,
        help="Path to sources.yaml (default: <root>/sources.yaml)",
    )

    draft_p = sub.add_parser(
        "draft",
        help="Draft candidates.md for a week (from fetch raw or --fixture)",
    )
    draft_p.add_argument("--fixture", type=Path, default=None)
    draft_p.add_argument("--root", type=Path, default=None)
    draft_p.add_argument("--week", type=str, default=None)
    draft_p.add_argument("--since", type=str, default=None)
    draft_p.add_argument("--until", type=str, default=None)
    draft_p.add_argument(
        "--fallback",
        action="store_true",
        help="Force no-LLM drafting",
    )

    finalize_p = sub.add_parser("finalize", help="Write digest.md from candidates.md")
    finalize_p.add_argument("--week", type=str, required=True)
    finalize_p.add_argument("--root", type=Path, default=None)

    return parser


def _cmd_assemble(args: argparse.Namespace) -> int:
    meta, items = load_week_fixture(args.fixture)
    assembled = assemble_week(items, meta)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(assembled.digest_markdown, encoding="utf-8")
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(assembled.digest_markdown)
    return 0


def _cmd_fetch(args: argparse.Namespace, root: Path) -> int:
    window = _window_from_args(args)
    week_dir = ensure_week_dir(root, window.week_id)
    fetched = fetch_from_sources(
        root,
        window,
        sources_path=args.sources,
        offline=args.offline,
    )
    write_fetch_artifacts(week_dir, fetched, window)
    kept, skipped = filter_duplicates(fetched.items, root)
    meta = WeekMeta(
        week_id=window.week_id,
        date_start=window.date_start.isoformat(),
        date_end=window.date_end.isoformat(),
        tagline="（待補：本週標語）",
        source_count=fetched.source_count,
    )
    write_items_json(week_dir / "items.json", meta, kept)
    # Remember all fetched survivors so unchecked URLs do not re-enter next week.
    for item in kept:
        item.selected = True
    remember_items(kept, root, week_id=meta.week_id)
    print(f"Week: {window.week_id}", file=sys.stderr)
    print(
        f"Fetched items: {len(fetched.items)}; after dedup: {len(kept)}",
        file=sys.stderr,
    )
    if skipped:
        print(f"Dedup skipped: {len(skipped)}", file=sys.stderr)
    if fetched.errors:
        print("Fetch notes/errors:", file=sys.stderr)
        for err in fetched.errors:
            print(f"  - {err}", file=sys.stderr)
    print(f"Wrote {week_dir / 'raw' / 'fetch.json'}", file=sys.stderr)
    print(f"Wrote {week_dir / 'items.json'}", file=sys.stderr)
    return 0 if kept or fetched.items else 1


def _cmd_draft(args: argparse.Namespace, root: Path, parser: argparse.ArgumentParser) -> int:
    if args.fixture:
        meta, items = load_week_fixture(args.fixture)
        window = _window_from_args(args)
        if args.week or (args.since and args.until):
            meta = WeekMeta(
                week_id=window.week_id,
                date_start=window.date_start.isoformat(),
                date_end=window.date_end.isoformat(),
                tagline=meta.tagline,
                header_rel_path=meta.header_rel_path,
                source_count=meta.source_count,
            )
    else:
        if not args.week:
            parser.error("draft without --fixture requires --week")
        week_dir = root / "weeks" / str(args.week)
        meta, items = read_items_json(week_dir / "items.json")

    week_dir = ensure_week_dir(root, meta.week_id)
    items, meta = draft_items(
        items,
        meta,
        force_fallback=bool(args.fallback) or not llm_enabled(),
        cache_dir=week_dir / "raw",
    )
    path = write_candidates(week_dir, meta, items)
    print(f"Wrote {path}", file=sys.stderr)
    return 0


def _cmd_finalize(args: argparse.Namespace, root: Path) -> int:
    week_dir = root / "weeks" / str(args.week)
    if not (week_dir / "candidates.md").exists():
        print(f"Missing candidates.md in {week_dir}", file=sys.stderr)
        return 1
    out = finalize_week(week_dir)
    meta, items = read_items_json(week_dir / "items.json")
    remember_items(items, root, week_id=meta.week_id)
    print(f"Wrote {out}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root) if getattr(args, "root", None) else project_root_from_cwd()

    if args.command == "assemble":
        return _cmd_assemble(args)
    if args.command == "fetch":
        return _cmd_fetch(args, root)
    if args.command == "draft":
        return _cmd_draft(args, root, parser)
    if args.command == "finalize":
        return _cmd_finalize(args, root)
    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
