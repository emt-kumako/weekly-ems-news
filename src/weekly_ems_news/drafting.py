from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from weekly_ems_news.models import NewsItem, PICO, WeekMeta, WhyLabel


def apply_fallback_drafts(items: list[NewsItem], meta: WeekMeta) -> list[NewsItem]:
    """No-LLM path: keep excerpts; mark human-needed fields clearly."""
    _ = meta  # tagline handled by caller via fallback_tagline
    for item in items:
        if not item.summary:
            item.summary = "（抓取降級：無摘要，請補）"
        if not item.next_move.strip() or item.next_move.startswith("（待補"):
            item.next_move = "（待補：為何重要／現場下一動）"
    return items


def fallback_tagline(items: list[NewsItem]) -> str:
    if not items:
        return "（待補：本週標語）"
    pillars = sorted({i.pillar.value for i in items})
    return f"本週候選涵蓋{'／'.join(pillars)}（無 LLM，請改寫標語）"


def llm_enabled() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY") or os.environ.get("WEEKLY_EMS_API_KEY"))


def _openai_chat(prompt: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("WEEKLY_EMS_API_KEY")
    model = os.environ.get("WEEKLY_EMS_MODEL", "gpt-4o-mini")
    body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是台灣院前緊急醫療編輯。用繁體中文撰寫簡潔週報草稿。"
                    "只輸出 JSON。"
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    content = payload["choices"][0]["message"]["content"]
    if not isinstance(content, str):
        raise ValueError("LLM response content is not a string")
    return content


def apply_llm_drafts(items: list[NewsItem], meta: WeekMeta) -> tuple[list[NewsItem], str]:
    """Best-effort LLM drafting; falls back per-item on failure."""
    catalog = [
        {
            "id": i.id,
            "title": i.title,
            "source": i.source,
            "summary": i.summary,
            "pillar": i.pillar.value,
            "has_pico": i.pico is not None,
        }
        for i in items
    ]
    prompt = (
        "為下列 EMS 候選條目各寫：why_label（改做法|跟上認知|教學可用）、"
        "next_move（一句現場下一動）、必要時 refined_summary；"
        "若 has_pico 為 true 或內容像研究／指引，另給 pico"
        "（population/intervention/comparison/outcome）。\n"
        "並給 week_tagline 一句。輸出 JSON："
        '{"tagline":"...","items":[{"id":"...","why_label":"...",'
        '"next_move":"...","summary":null,'
        '"pico":{"population":"","intervention":"","comparison":"","outcome":""}}]}\n\n'
        f"{json.dumps(catalog, ensure_ascii=False)}"
    )
    try:
        raw = _openai_chat(prompt)
        # Allow fenced JSON
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
            raw = raw.rsplit("```", 1)[0]
        data = json.loads(raw)
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError, ValueError):
        apply_fallback_drafts(items, meta)
        return items, fallback_tagline(items)

    by_id = {i.id: i for i in items}
    for row in data.get("items", []):
        item = by_id.get(row.get("id"))
        if not item:
            continue
        if row.get("why_label") in {"改做法", "跟上認知", "教學可用"}:
            item.why_label = WhyLabel(row["why_label"])
        if row.get("next_move"):
            item.next_move = row["next_move"]
        if row.get("summary"):
            item.summary = row["summary"]
        pico_row = row.get("pico")
        if isinstance(pico_row, dict) and all(
            pico_row.get(k)
            for k in ("population", "intervention", "comparison", "outcome")
        ):
            item.pico = PICO(
                population=str(pico_row["population"]),
                intervention=str(pico_row["intervention"]),
                comparison=str(pico_row["comparison"]),
                outcome=str(pico_row["outcome"]),
            )
    tagline = data.get("tagline") or fallback_tagline(items)
    return items, tagline


def draft_items(
    items: list[NewsItem],
    meta: WeekMeta,
    *,
    force_fallback: bool = False,
    cache_dir: Path | None = None,
) -> tuple[list[NewsItem], WeekMeta]:
    if force_fallback or not llm_enabled():
        apply_fallback_drafts(items, meta)
        tagline = (
            meta.tagline
            if meta.tagline and not meta.tagline.startswith("（待補")
            else fallback_tagline(items)
        )
    else:
        items, tagline = apply_llm_drafts(items, meta)

    new_meta = WeekMeta(
        week_id=meta.week_id,
        date_start=meta.date_start,
        date_end=meta.date_end,
        tagline=tagline,
        header_rel_path=meta.header_rel_path,
        source_count=meta.source_count,
    )
    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = cache_dir / "drafts.json"
        cache_path.write_text(
            json.dumps(
                {
                    "tagline": tagline,
                    "items": [
                        {
                            "id": i.id,
                            "why_label": i.why_label.value,
                            "next_move": i.next_move,
                            "summary": i.summary,
                        }
                        for i in items
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return items, new_meta
