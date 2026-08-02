Status: ready-for-agent
Type: spec
Feature: weekly-ems-news

# Weekly EMS News — Spec

## Problem Statement

I work in and around emergency medical services and need a reliable weekly way to surface what actually matters for prehospital practice in Taiwan—without drowning in international journals, press releases, or off-topic hospital specialty noise. Today that means ad‑hoc browsing, inconsistent notes, and no durable weekly artifact I can re-read or later reshape into teaching material.

## Solution

A personal, semi-automated **Weekly EMS News** tool that, for each calendar week, gathers high-signal items from a small curated source list, drafts Traditional Chinese candidate entries, lets me select and lightly edit them, and finalizes a branded Markdown digest of at most ten items—balanced across clinical, system/operations, and equipment when material exists—with clear “why it matters” framing for the field. All editorial history lives in one project folder, packaged per week.

## User Stories

1. As a prehospital clinician, I want a weekly digest of at most ten EMS items, so that I can finish reading it in one short sitting.
2. As a prehospital clinician, I want the digest written in Traditional Chinese, so that I can scan it quickly without translating on the fly.
3. As a prehospital clinician, I want each item to state why it matters with a practice-impact label and one “next move” sentence, so that I know whether to change practice, update my mental model, or save it for teaching.
4. As a prehospital clinician, I want clinical, system/operations, and equipment coverage when material exists, so that one theme does not dominate the week.
5. As a prehospital clinician, I want empty topic sections omitted, so that the digest does not pad with “nothing this week” noise.
6. As a prehospital clinician, I want Taiwan and Chinese-speaking local practice prioritized, so that the digest stays actionable where I work.
7. As a prehospital clinician, I want international items only when they may change universal care, foreshadow local follow-through, or offer comparable equipment/system lessons, so that foreign novelty does not flood the list.
8. As a prehospital clinician, I want non-Taiwan Chinese sources treated with the same bar as other foreign sources, so that language familiarity is not mistaken for local applicability.
9. As a prehospital clinician, I want the clinical lens centered on prehospital care including handover-relevant hospital information, so that in-hospital specialty depth does not crowd out field practice.
10. As a prehospital clinician, I want clinical subtopics among resuscitation, trauma, and common medical emergencies rotated fairly within a week, so that one subtopic does not consume the clinical quota.
11. As a prehospital clinician, I want pediatrics, obstetrics, behavioral health/self-harm, and disaster/MCI items only on major updates, so that specialty noise stays out unless it truly matters.
12. As a system-minded practitioner, I want system items focused on regulation/scope, dispatch/transport, and training/credentialing, so that operations updates are easy to find.
13. As a field clinician, I want equipment items backed by evidence, norms, recalls, standards, or locally comparable trials—not vendor marketing—so that product hype does not appear as news.
14. As a careful reader, I want marketing, HR fluff, single-hospital promo, irrelevant biotech stock noise, off-topic specialty detail, and duplicate republishing excluded, so that candidates stay trustworthy.
15. As a careful reader, I want research inclusion weighted toward guidelines, reviews, large trials, and practice-relevant observational/safety/negative findings, so that weak early science does not dominate.
16. As a careful reader, I want preprints, meeting abstracts, and scoop coverage included only when high-impact and clearly marked as unverified, so that I do not treat unsettled claims as settled.
17. As an editor of my own digest, I want same-topic clusters merged into one item with related links by default, so that republishing waves do not waste slots.
18. As an editor of my own digest, I want conflicting conclusions or “primary source vs local interpretation” pairs split into separate items with an explicit relationship note, so that I do not blur disagreement.
19. As an editor of my own digest, I want a semi-automated flow where the tool drafts candidates and I select/edit before finalize, so that I keep accuracy control without writing everything from scratch.
20. As an editor of my own digest, I want to run the weekly update manually at first, so that I can intervene when sources or drafts misbehave.
21. As an editor of my own digest, I want the design to allow later scheduling without rework, so that I can automate the trigger later.
22. As an editor of my own digest, I want calendar-week defaults with override date bounds, so that late sources or catch-up runs still work.
23. As an editor of my own digest, I want a candidates document with checkboxes and editable drafts, so that selection happens in one place.
24. As an editor of my own digest, I want finalize to produce a digest while preserving the candidates file, so that each week keeps an editorial history.
25. As an editor of my own digest, I want per-week packaging of raw metadata, candidates, and digest, so that I can reopen any week as a unit.
26. As an editor of my own digest, I want shared branding assets and a source list at project level, so that weeks stay consistent without copying config each time.
27. As a reader, I want the digest to open with the Weekly EMS News header image, week identity, and a one-line tagline, so that each issue feels like a finished product.
28. As a reader, I want a short overview of one bullet per present section, so that I know the week’s shape before diving in.
29. As a reader, I want overview bullets omitted for missing sections, so that the overview matches the body.
30. As a reader, I want compact item cards with title link, meta line, summary or PICO, and why-it-matters, so that scanning stays fast.
31. As a reader, I want research/guideline items summarized in PICO form and other items in ordinary summary form, so that evidence and news are each readable in the right shape.
32. As a reader, I want an appendix for related links, unverified items listing, and production metadata, so that the main columns stay clean.
33. As a reader, I want items ordered with “change practice” first within a section, then by local groundedness, so that the most actionable items appear first.
34. As a future trainer, I want topic tags on every item now, so that I can later filter into teaching packs without re-tagging history.
35. As a future trainer, I want durable digests in Markdown, so that I can export or reshape them into lesson material later without a teaching system in v1.
36. As an operator of the tool, I want a small v1 source list of about eight to twelve official, society, journal, and guideline sources, so that candidate volume stays reviewable.
37. As an operator of the tool, I want drafts from an LLM API when configured, so that summaries, PICO, taglines, and why-it-matters start from a usable draft.
38. As an operator of the tool, I want a no-key fallback that still produces candidates from metadata and short excerpts, so that a missing API key does not block the week.
39. As an operator of the tool, I want long-term storage of metadata and short excerpts—not full-text archives—so that I can re-draft without becoming a copyright dumping ground.
40. As an operator of the tool, I want optional retention of LLM drafts that can be regenerated, so that I can rerun drafting without refetching forever.
41. As an operator of the tool, I want strict deduplication of canonical URLs across weeks, with re-entry allowed for major updates or local follow-through, so that repeats stay rare but meaningful second waves can appear.
42. As an operator of the tool, I want Python CLI commands for fetch, draft, and finalize, so that the workflow matches a simple personal tool.
43. As an operator of the tool, I want sources declared in a YAML list, so that I can add or remove feeds without code changes.
44. As a maintainer, I want selection and layout rules enforced in digest assembly, so that finalize cannot silently violate the weekly contract.
45. As a maintainer, I want tests at the week-assembly seam with fixtures, so that layout and selection behavior stay stable without live network or LLM calls.
46. As a maintainer, I want fetch and LLM behind adapters, so that offline fixtures can drive the same assembly path.
47. As a user returning next month, I want prior weeks retained on disk, so that I can compare what changed over time.
48. As a user in a thin news week, I want fewer than ten items when quality is lacking, so that the tool never invents filler to hit a quota.
49. As a user in a rich news week, I want ranking to cut to ten after guaranteeing one item per populated pillar when possible, so that balance and the cap coexist.
50. As a reader of clinical content, I want resuscitation, trauma, and medical emergencies all eligible, so that everyday prehospital medicine is covered—not only arrest care.
51. As a Taiwan-focused reader, I want central government and national society updates preferred, with local government items only when likely to diffuse or change common practice, so that county noise stays filtered.
52. As an editor, I want to reorder candidate blocks manually before finalize, so that automatic ordering never traps a better narrative sequence.
53. As an editor, I want production metadata in the appendix (date window, source count), so that I can audit how a week was produced.
54. As a future scheduler, I want week identity and output paths determined from inputs rather than interactive prompts only, so that cron or automation can call the same commands later.
55. As a brand-conscious user, I want the existing Weekly EMS News header asset reused at the top of each digest, so that issues look consistent.
56. As a solo user, I want everything under one project root for this tool, so that editorial history is not scattered across apps.
57. As a careful consumer of unsettled science, I want unverified markers visible on cards and listed in the appendix when present, so that uncertainty is hard to miss.
58. As an implementer, I want a clear out-of-scope boundary excluding web UI, Notion, email delivery, professional media/social sources in v1, and a full teaching-card system, so that v1 stays shippable.
59. As an implementer, I want domain language stabilized around digest, candidates, pillars, groundedness, and why-it-matters labels, so that code and docs do not invent synonyms.
60. As a future me preparing a class, I want past digests searchable by week folder naming, so that I can grab a specific ISO week quickly.

## Implementation Decisions

- Build a greenfield **Python CLI** personal tool with three primary actions conceptually: gather sources for a week window, draft candidate entries, and finalize a digest from selected candidates.
- Keep all runtime editorial artifacts under a single project root chosen by the user; package each week as one week folder containing raw/normalized metadata, the candidates document, and the digest document.
- Maintain project-level shared assets (including the Weekly EMS News header image) and a YAML source registry for the v1 list of roughly eight to twelve official/society/journal/guideline sources.
- Default the week window to a calendar week identity suitable for folder naming; allow since/until overrides for catch-up runs.
- Model each item with a minimal field set: title, source, date, link, summary or PICO, why-it-matters label (`改做法` / `跟上認知` / `教學可用`), one next-move sentence, and pillar tag (`臨床` / `系統` / `裝備`). Optional flags for unverified status and related links / merge relationships.
- Apply **selection policy** during candidate ranking and finalize: prehospital-first including handover-relevant hospital content; Taiwan-first groundedness; foreign and non-Taiwan Chinese sources only with universal-care, likely local follow-through, or comparable equipment/system rationale; exclusions for marketing/HR/promo/biotech-noise/off-topic specialty/duplicate republish; research bar as agreed; special populations only on major updates; same-topic merge by default with split on conflict or primary-vs-local interpretation.
- Cap finalized items at **ten**. Soft balance: when material exists, include at least one clinical, one system, and one equipment item; within clinical, rotate resuscitation/trauma/medical emergencies and keep any single clinical subtopic to at most half of that week’s clinical count.
- Sort within each pillar by why-it-matters (change-practice first) then groundedness; preserve manual order overrides from the candidates document when present.
- Render digests as Markdown with: header image, week label/date, one-line tagline; overview bullets only for pillars that have items; pillar sections with empty pillars omitted; compact cards; PICO block for research/guideline items; appendix for related links, unverified listing, and production metadata.
- Candidates workflow: single candidates Markdown with checkbox selection and inline edits; finalize writes the digest and leaves candidates intact as history.
- LLM drafting is an adapter: when credentials exist, draft Traditional Chinese summary/PICO, why-it-matters, and weekly tagline; when absent, fall back to metadata plus short excerpts and leave human-completed fields obvious.
- Persist metadata and short excerpts long-term; allow regenerable draft caches; do not aim to archive full article bodies.
- Deduplicate on canonical URL across weeks; allow re-entry when marked as major update or local follow-through (relationship to prior item recorded).
- **Primary test seam (sole):** `assemble_week` — given normalized items plus week context (fixtures), produce candidates and digest Markdown whose observable structure and rules match this spec. Network fetch and LLM calls stay outside this seam behind adapters.

## Testing Decisions

- Good tests assert **external behavior** at `assemble_week`: resulting Markdown structure and selection/layout invariants, not private helpers, prompt strings, or HTTP details.
- Cover with fixtures at minimum: max-ten enforcement; pillar balance when material exists; omission of empty pillars and matching overview bullets; compact card fields; PICO vs ordinary summary branching; appendix contents; within-pillar ordering; merge vs split representation; unverified markers; calendar week identity rendering with header/tagline; sub-ten digests when inputs are sparse; clinical subtopic half-cap behavior when relevant fixtures are provided.
- Prefer one seam and many fixtures over many mocked unit layers.
- No prior art in-repo (greenfield); establish the first test suite around `assemble_week` as the template for later adapter tests if added.
- Live source fetch and live LLM are out of the default automated suite; optional smoke checks may exist later but are not required for v1 readiness.

## Out of Scope

- Web UI, Notion sync, email delivery, and other non-Markdown reading surfaces
- Teaching-card fields (audience, quiz prompts, difficulty) and a full training CMS
- Professional media and social/forum sources in v1
- Full-text long-term article archival
- Fully automatic publish without human selection
- Scheduled/cron execution in v1 (design must not preclude it)
- Multi-user collaboration, accounts, or permissions
- Guaranteeing every pillar every week regardless of material quality
- Non-EMS domains and Electronics Manufacturing Services content
- Perfect bilingual digests or English-primary output
- Mobile apps and push notifications

## Further Notes

- Branding asset already exists in the project assets area as the Weekly EMS News header; digests should reference it relatively from week folders.
- Future teaching use is an explicit design constraint (durable Markdown, tags, PICO for evidence) but not a v1 feature build.
- Issue tracking for this repo is local Markdown under `.scratch/`; this spec is the agent-ready contract for implementation.
- Suggested implementation order after this spec: normalize item schema and `assemble_week` + tests → candidates/finalize CLI wiring → source fetch adapters → LLM draft adapter → seed YAML sources → first real week dry run with human edit.

## Comments

- Published from grilling + confirmation session; primary seam and local tracker agreed by maintainer before publish.
