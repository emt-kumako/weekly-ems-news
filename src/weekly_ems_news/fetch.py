from __future__ import annotations

import json
import re
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

import certifi

from weekly_ems_news.fixtures import load_week_fixture
from weekly_ems_news.models import NewsItem, Pillar, WhyLabel
from weekly_ems_news.sources import Source, enabled_sources
from weekly_ems_news.week import WeekWindow


class _TitleDescParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_title = False
        self.title = ""
        self.description = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_d = {k: (v or "") for k, v in attrs}
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            name = (attrs_d.get("name") or attrs_d.get("property") or "").lower()
            if name in {"description", "og:description"} and attrs_d.get("content"):
                if not self.description:
                    self.description = attrs_d["content"].strip()

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data


@dataclass
class FetchResult:
    items: list[NewsItem] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    source_count: int = 0


def _short_excerpt(text: str, limit: int = 280) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _ssl_context() -> ssl.SSLContext:
    return ssl.create_default_context(cafile=certifi.where())


def _fetch_html(url: str, timeout: float = 20.0) -> tuple[str, str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "WeeklyEMSNews/0.1 (+local; personal digest tool)"},
    )
    with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        html = resp.read().decode(charset, errors="replace")
    parser = _TitleDescParser()
    parser.feed(html)
    title = parser.title.strip() or urlparse(url).netloc
    excerpt = parser.description or _short_excerpt(
        re.sub(r"<[^>]+>", " ", html)[:2000]
    )
    return title, _short_excerpt(excerpt)


def _item_from_page(source: Source, title: str, excerpt: str) -> NewsItem:
    pillar = Pillar(source.pillars[0]) if source.pillars else Pillar.SYSTEM
    groundedness = 8 if source.region == "tw" else 2
    return NewsItem(
        id=f"{source.id}-{abs(hash(source.url)) % 10_000_000}",
        title=title,
        url=source.url,
        source=source.name,
        date="",  # filled by caller with window end if empty
        pillar=pillar,
        why_label=WhyLabel.UPDATE_KNOWLEDGE,
        next_move="",
        summary=excerpt or "（抓取降級：僅有標題／短摘錄，請補為何重要）",
        groundedness=groundedness,
        selected=True,
    )


def fetch_from_sources(
    project_root: Path,
    window: WeekWindow,
    *,
    sources_path: Path | None = None,
    offline: bool = False,
) -> FetchResult:
    path = sources_path or (project_root / "sources.yaml")
    sources = enabled_sources(path)
    result = FetchResult(source_count=len(sources))
    date_str = window.date_end.isoformat()

    for source in sources:
        if source.type == "fixture" or source.url.startswith("fixture://"):
            if not source.fixture:
                result.errors.append(f"{source.id}: fixture source missing path")
                continue
            fixture_path = project_root / source.fixture
            try:
                _, items = load_week_fixture(fixture_path)
            except Exception as exc:  # noqa: BLE001 — surface in fetch log
                result.errors.append(f"{source.id}: {exc}")
                continue
            for item in items:
                if not item.date:
                    item.date = date_str
                result.items.append(item)
            continue

        if offline:
            result.errors.append(f"{source.id}: skipped (offline mode)")
            continue

        try:
            title, excerpt = _fetch_html(source.url)
            item = _item_from_page(source, title, excerpt)
            item.date = date_str
            result.items.append(item)
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            result.errors.append(f"{source.id}: {exc}")

    return result


def write_fetch_artifacts(
    week_dir: Path,
    result: FetchResult,
    window: WeekWindow,
) -> Path:
    week_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = week_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    payload = {
        "week_id": window.week_id,
        "date_start": window.date_start.isoformat(),
        "date_end": window.date_end.isoformat(),
        "source_count": result.source_count,
        "item_count": len(result.items),
        "errors": result.errors,
        "items": [
            {
                "id": i.id,
                "title": i.title,
                "url": i.url,
                "source": i.source,
                "date": i.date,
                "summary": i.summary,
            }
            for i in result.items
        ],
    }
    path = raw_dir / "fetch.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
