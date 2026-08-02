from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from weekly_ems_news.assemble import assemble_week_auto
from weekly_ems_news.codec import load_items
from weekly_ems_news.pipeline import (
    run_draft,
    run_fetch,
    run_finalize,
    run_rebuild_reading_surface,
)
from weekly_ems_news.week import WeekWindow, iso_week_window, window_from_bounds


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

    fetch_p = sub.add_parser("fetch", help="run_fetch for a week package")
    fetch_p.add_argument("--root", type=Path, default=None)
    fetch_p.add_argument("--week", type=str, default=None)
    fetch_p.add_argument("--since", type=str, default=None)
    fetch_p.add_argument("--until", type=str, default=None)
    fetch_p.add_argument("--offline", action="store_true")
    fetch_p.add_argument("--sources", type=Path, default=None)

    draft_p = sub.add_parser("draft", help="run_draft for a week package")
    draft_p.add_argument("--fixture", type=Path, default=None)
    draft_p.add_argument("--root", type=Path, default=None)
    draft_p.add_argument("--week", type=str, default=None)
    draft_p.add_argument("--since", type=str, default=None)
    draft_p.add_argument("--until", type=str, default=None)
    draft_p.add_argument("--fallback", action="store_true")

    finalize_p = sub.add_parser("finalize", help="run_finalize for a week package")
    finalize_p.add_argument("--week", type=str, required=True)
    finalize_p.add_argument("--root", type=Path, default=None)

    rebuild_p = sub.add_parser(
        "rebuild-reading",
        help="Rebuild reading/index.html from existing digests (no fetch)",
    )
    rebuild_p.add_argument("--root", type=Path, default=None)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root) if getattr(args, "root", None) else project_root_from_cwd()

    if args.command == "assemble":
        meta, items = load_items(args.fixture)
        assembled = assemble_week_auto(items, meta)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(assembled.digest_markdown, encoding="utf-8")
            print(f"Wrote {args.output}", file=sys.stderr)
        else:
            sys.stdout.write(assembled.digest_markdown)
        return 0

    if args.command == "fetch":
        result = run_fetch(
            root,
            _window_from_args(args),
            sources_path=args.sources,
            offline=args.offline,
        )
        print(f"Week: {result.week_id}", file=sys.stderr)
        print(result.message, file=sys.stderr)
        return 0 if result.ok else 1

    if args.command == "draft":
        window = None
        if args.week or (args.since and args.until):
            window = _window_from_args(args)
        if not args.fixture and not args.week:
            parser.error("draft without --fixture requires --week")
        result = run_draft(
            root,
            week_id=args.week,
            fixture=args.fixture,
            window=window if args.fixture else None,
            force_fallback=bool(args.fallback),
        )
        print(result.message, file=sys.stderr)
        return 0 if result.ok else 1

    if args.command == "finalize":
        result = run_finalize(root, str(args.week))
        print(result.message, file=sys.stderr)
        return 0 if result.ok else 1

    if args.command == "rebuild-reading":
        result = run_rebuild_reading_surface(root)
        print(result.message, file=sys.stderr)
        return 0 if result.ok else 1

    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
