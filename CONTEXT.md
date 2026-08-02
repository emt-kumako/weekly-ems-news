# Weekly EMS News

Personal tooling context for a Taiwan-focused prehospital EMS weekly digest.

## Language

**Digest**:
The finalized Traditional Chinese weekly Markdown report (at most ten items), organized by pillar.
_Avoid_: Newsletter, report, briefing

**Candidates**:
The human-editable Markdown checklist for one week; selection and copy edits happen here before finalize.
_Avoid_: Draft queue, inbox, staging list

**Week package**:
One week’s on-disk bundle: raw fetch metadata, normalized items, candidates, and digest.
_Avoid_: Issue folder, edition archive

**Pillar**:
One of the three digest sections: 臨床, 系統, or 裝備.
_Avoid_: Category, topic bucket, column (except in layout talk)

**Why-it-matters**:
The practice-impact label (`改做法` / `跟上認知` / `教學可用`) plus one next-move sentence for the field.
_Avoid_: Summary blurb, takeaway alone

**Week-stage pipeline**:
The orchestration of fetch → draft → finalize for a week package.
_Avoid_: Workflow service, job runner

**Assemble week**:
Turning normalized items and week metadata into digest Markdown (merge, selection, and rendering inside).
_Avoid_: Renderer pipeline, markdown builder (as the domain name)

**Dedup store**:
The remembered set of canonical URLs already seen across weeks, including re-entry for major updates.
_Avoid_: Cache, index, database

**Source transport**:
How raw material is obtained from a configured source before it becomes a normalized item.
_Avoid_: Scraper service, connector API
