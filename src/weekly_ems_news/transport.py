from __future__ import annotations

import re
import ssl
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlparse

import certifi

from weekly_ems_news.sources import Source


@dataclass(frozen=True)
class RawMaterial:
    title: str
    excerpt: str
    url: str
    fetched_at: str
    source_id: str


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


def _short_excerpt(text: str, limit: int = 280) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _ssl_context() -> ssl.SSLContext:
    return ssl.create_default_context(cafile=certifi.where())


def fetch_http(source: Source, *, timeout: float = 20.0) -> RawMaterial:
    req = urllib.request.Request(
        source.url,
        headers={"User-Agent": "WeeklyEMSNews/0.1 (+local; personal digest tool)"},
    )
    with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        html = resp.read().decode(charset, errors="replace")
    parser = _TitleDescParser()
    parser.feed(html)
    title = parser.title.strip() or urlparse(source.url).netloc
    excerpt = parser.description or _short_excerpt(
        re.sub(r"<[^>]+>", " ", html)[:2000]
    )
    return RawMaterial(
        title=title,
        excerpt=_short_excerpt(excerpt),
        url=source.url,
        fetched_at=_now_iso(),
        source_id=source.id,
    )


def is_fixture_source(source: Source) -> bool:
    return source.type == "fixture" or source.url.startswith("fixture://")
