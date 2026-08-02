from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Pillar(str, Enum):
    CLINICAL = "臨床"
    SYSTEM = "系統"
    EQUIPMENT = "裝備"


class WhyLabel(str, Enum):
    CHANGE_PRACTICE = "改做法"
    UPDATE_KNOWLEDGE = "跟上認知"
    TEACHING = "教學可用"


class ClinicalSubtopic(str, Enum):
    RESUSCITATION = "復甦"
    TRAUMA = "創傷"
    MEDICAL = "內科急症"
    SPECIAL = "特殊情境"


WHY_SORT_RANK = {
    WhyLabel.CHANGE_PRACTICE: 0,
    WhyLabel.UPDATE_KNOWLEDGE: 1,
    WhyLabel.TEACHING: 2,
}


@dataclass(frozen=True)
class PICO:
    population: str
    intervention: str
    comparison: str
    outcome: str


@dataclass
class NewsItem:
    """Normalized digest item ready for assembly."""

    id: str
    title: str
    url: str
    source: str
    date: str
    pillar: Pillar
    why_label: WhyLabel
    next_move: str
    summary: str | None = None
    pico: PICO | None = None
    clinical_subtopic: ClinicalSubtopic | None = None
    unverified: bool = False
    related_urls: list[str] = field(default_factory=list)
    relationship_note: str | None = None
    groundedness: int = 0
    selected: bool = True
    allow_reentry: bool = False
    update_of: str | None = None
    canonical_url: str | None = None

    def url_key(self) -> str:
        return (self.canonical_url or self.url).strip()


@dataclass(frozen=True)
class WeekMeta:
    week_id: str
    date_start: str
    date_end: str
    tagline: str
    header_rel_path: str = "../../assets/weekly-ems-news-header.png"
    source_count: int | None = None


@dataclass(frozen=True)
class WeekAssembly:
    """Observable output of the assemble_week seam."""

    week_id: str
    digest_markdown: str
    digest_html: str
    item_ids: tuple[str, ...]
