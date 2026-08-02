Status: ready-for-agent
Type: spec
Feature: digest-reading-surface

# Digest reading surface (HTML) — Spec

## Problem Statement

I already produce a weekly EMS digest as Markdown inside each week package, and I have a brand header image, but Markdown preview is not a comfortable place to *read* the week. I want to open a local, easy-on-the-eyes page that shows the digest with proper layout, and quickly jump between weeks—defaulting to the calendar week of the day I open it—without building a hosted website or changing how I edit candidates.

## Solution

Add a **local reading surface**: static HTML generated into the project (and/or each week package) that presents the finalized digest in a comfortable layout using the existing Weekly EMS News header image, overview, pillars, compact cards, and appendix. A week list lets me pick any week that has a digest; when I open the surface, it defaults to the ISO calendar week for “today” (or a clear empty state if that week has no digest yet). Markdown digests remain the editorial source of truth; HTML is the reading view. No accounts, no server required beyond opening files in a browser (file:// or a trivial local open).

## User Stories

1. As a reader, I want a comfortable HTML view of my weekly digest, so that I can scan pillars and cards without fighting editor chrome.
2. As a reader, I want the brand header image at the top of the reading view, so that each week feels like the same product.
3. As a reader, I want week identity, date range, and tagline visible near the header, so that I know which week I am reading.
4. As a reader, I want overview bullets for pillars that have items, so that I grasp the week before scrolling.
5. As a reader, I want clinical / system / equipment sections with empty pillars omitted, so that the page stays clean.
6. As a reader, I want compact cards with title link, meta, summary or PICO, and why-it-matters, so that each item is scannable.
7. As a reader, I want unverified items clearly marked, so that I do not treat unsettled claims as settled.
8. As a reader, I want the appendix (related links, unverified list, production meta) available but visually secondary, so that the main columns stay primary.
9. As a reader, I want typography, spacing, and contrast tuned for longer reading, so that a ten-item week is not fatiguing.
10. As a reader, I want the layout to work on a laptop browser window, so that I can read without horizontal scroll.
11. As a reader, I want a usable layout on a phone browser, so that I can skim a week on the go.
12. As a reader, I want a week list of available digests, so that I can jump to prior weeks without hunting folders.
13. As a reader, I want the week list ordered newest-first (by week id / calendar), so that recent weeks are easy to find.
14. As a reader, I want the default selection to be the ISO calendar week containing “today” when I open the surface, so that I land on this week automatically.
15. As a reader, I want a clear empty state when today’s week has no digest yet, so that I know I still need to finalize (with a path to pick another week).
16. As a reader, I want selecting another week to show that week’s digest without leaving the reading surface, so that comparison across weeks is fast.
17. As a reader, I want the currently selected week highlighted in the list, so that I do not lose my place.
18. As a reader, I want weeks without a digest omitted from the selectable list (or marked unavailable), so that I do not open broken links.
19. As an editor, I want HTML regenerated when I finalize a week, so that the reading view stays in sync with candidates I just locked.
20. As an editor, I want Markdown `digest.md` to keep being written, so that git-friendly editing and diffs remain available.
21. As an editor, I want regenerating the reading surface after multiple finalizes to refresh the week list, so that new weeks appear without manual HTML edits.
22. As an operator, I want a simple way to open the reading surface (documented path or CLI helper), so that I do not have to remember nested folders.
23. As an operator, I want assets (header image) to resolve correctly from the HTML location, so that the brand image is not broken under file://.
24. As an operator, I want generation to work offline from local week packages, so that reading does not depend on network fetch.
25. As a maintainer, I want HTML generation tested without a real browser automation suite, so that CI stays fast and deterministic.
26. As a maintainer, I want the reading surface to reuse assembled digest content rather than re-implementing selection rules, so that Markdown and HTML cannot disagree on which items made the cut.
27. As a maintainer, I want a single primary test seam for the reading surface, so that layout and week-default behavior stay stable.
28. As a reader, I want links in cards to open the original sources, so that I can drill into primary material.
29. As a reader, I want Traditional Chinese body copy preserved exactly as in the digest, so that meaning is not re-translated by the HTML step.
30. As a reader, I want print/PDF-from-browser to be acceptable (basic print stylesheet optional), so that I can archive a week on paper if needed.
31. As a future trainer, I want past weeks still reachable from the list, so that I can pull an old digest into teaching prep.
32. As a careful reader, I want why-it-matters labels visually distinct, so that `改做法` stands out from softer updates.
33. As an operator, I want finalize failure to not leave a half-updated index pointing at missing HTML, so that the week list stays trustworthy.
34. As a reader, I want custom week ids (catch-up windows) to appear in the list when they have digests, so that non-ISO folder names are not invisible.
35. As a reader, I want “today’s week” resolution to use the same calendar-week rules as the pipeline, so that CLI week folders and the default selection match.
36. As a maintainer, I want ADR-aligned module shape preserved (pipeline / week package / assemble), so that HTML is an additive reading adapter, not a second editorial system.
37. As a reader, I want no login or cloud dependency, so that the surface stays a personal local tool.
38. As an operator, I want regenerating HTML for one week to be possible without refetching sources, so that layout tweaks are cheap.
39. As a reader, I want the page title / tab label to include the week id, so that multiple tabs stay distinguishable.
40. As a reader, I want reduced motion / no flashy animation requirements, so that presence stays calm and readable.

## Implementation Decisions

- Extend the week package / finalize path so that producing a digest also produces (or refreshes) HTML for that week, while continuing to write Markdown digest as today.
- Add a **reading surface** entry document (project-level index/viewer) that lists week packages which contain a finalized digest and shows one week’s HTML body at a time.
- Default week selection: ISO calendar week containing the open-time “today,” consistent with existing week-window rules; if that week has no digest, show an empty state and still allow choosing another listed week.
- Prefer generating self-contained or path-stable HTML that works when opened locally; brand header uses the existing project asset.
- Do **not** re-run selection/merge in the HTML layer: render from the same assembled item set / digest content used for Markdown so the two views cannot diverge on membership.
- Primary test seam (sole for this feature): **`build_reading_surface`** (name may vary) — given a fixture project root with one or more week packages (items + finalized digest inputs as needed) and a fixed “today”, produce the index/viewer HTML and per-week digest HTML whose observable structure includes header branding, week list, default selection for today’s week (or empty state), and the digest sections/cards/appendix. Browser automation and visual screenshot diffs are out of the automated suite.
- CLI remains an adapter: e.g. finalize already triggers HTML refresh; optional explicit “rebuild reading surface” command is acceptable if it keeps the pipeline thin.
- Respect existing architecture ADRs: week-stage pipeline orchestration, week-package I/O, assemble entry points; HTML is a reading adapter behind week-package or a small adjacent module called from finalize—not a new editorial CMS.
- Styling: calm, readable typography and spacing; mobile-usable single column; avoid turning the surface into a dashboard of widgets.

## Testing Decisions

- Good tests assert external behavior at `build_reading_surface`: presence of brand image reference, week list membership/order, default week for a frozen “today”, empty-state when today’s week lacks a digest, and digest body structure (overview/pillars/cards/appendix cues) — not private CSS class names as the sole assertion strategy unless they encode contract.
- Prefer fixtures under tests that create temporary week package folders rather than live `weeks/` data.
- Prior art: existing assemble_week / pipeline fixture tests; extend the same style (filesystem fixtures, no network).
- Do not require Playwright/Selenium for v1 of this feature.

## Out of Scope

- Hosted website, auth, multi-user sharing, CMS
- Replacing Markdown digests entirely
- Changing selection/editorial rules in the HTML layer
- Email delivery, Notion sync, native mobile apps
- Full design-system / dark-mode productization (unless trivial via simple CSS)
- Guaranteeing bit-perfect print layout across browsers
- Interactive editing of candidates inside the HTML surface

## Further Notes

- Confirmed direction from product conversation: comfortable HTML (or equivalent) reading layout using the uploaded header image; plus a week selector list defaulting to the calendar week of open time.
- Domain vocabulary: Digest, Candidates, Week package, Pillar, Why-it-matters, Week-stage pipeline, Assemble week (see project glossary).
- Suggested build order: per-week digest HTML from assembled content → project reading surface with week list + default-today → wire into finalize / rebuild → fixture tests at `build_reading_surface`.

## Comments

- Seam proposal (static HTML + assemble reuse) agreed; week list + default current week added by maintainer before publish.
