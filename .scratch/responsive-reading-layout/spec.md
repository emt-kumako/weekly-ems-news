Status: ready-for-agent
Type: spec
Feature: responsive-reading-layout

# Responsive reading layout — Spec

## Problem Statement

I can already open a local HTML reading surface for Weekly EMS News digests, but I read on a laptop, sometimes on a tablet, and often skim on a phone. I want the same reading entry and week digests to stay comfortable across those sizes—without turning the tool into a hosted site or a full design system—so I am not fighting horizontal scroll or an unusable week list on a small screen.

## Solution

Keep (and lightly polish if needed) a **basic responsive layout** for the project reading surface and per-week digest HTML: desktop side rail + body; narrow viewports stack the week list above the digest and keep a single readable column; shared viewport and stylesheet cues so phone and tablet skimming work. Lock the contract at the existing `build_reading_surface` seam with fixture tests—no browser automation suite.

## User Stories

1. As a reader, I want the reading surface usable in a laptop browser window, so that I can read a week without horizontal scroll.
2. As a reader, I want a side week list on desktop, so that I can jump weeks while keeping the digest in view.
3. As a reader, I want the week list to move above the digest on narrow screens, so that the body gets full width on a phone or small tablet.
4. As a reader, I want week list items still tappable on a phone, so that I can change weeks with a thumb.
5. As a reader, I want digest cards and pillars to stack in one column on small screens, so that I can skim without pinching zoom.
6. As a reader, I want typography and padding to remain readable on phone, so that a ten-item week is not fatiguing.
7. As a reader, I want the brand header image to scale with the content width, so that branding does not overflow the viewport.
8. As a reader, I want the page to declare a proper mobile viewport, so that mobile browsers do not show a tiny desktop layout.
9. As a reader, I want tablet widths between phone and desktop to remain usable (stacked or comfortable hybrid), so that I do not need a third product layout.
10. As a reader, I want the currently selected week still recognizable after the list stacks, so that I do not lose my place.
11. As a reader, I want empty state copy readable on narrow screens, so that “today’s week not finalized” is clear on a phone.
12. As a reader, I want standalone week digest HTML to follow the same narrow-screen body rules, so that opening a single week file is still comfortable.
13. As a reader, I want links and why-it-matters blocks to remain scannable on mobile, so that I can act on next moves in the field.
14. As a reader, I want appendix content secondary but reachable on small screens, so that production meta does not dominate the fold.
15. As an operator, I want `rebuild-reading` (or finalize) to regenerate the responsive surface without refetch, so that layout tweaks are cheap.
16. As a maintainer, I want responsive behavior locked at `build_reading_surface`, so that regressions show up in fast fixture tests.
17. As a maintainer, I want tests to assert observable cues (viewport, layout structure, brand/body presence), not screenshot diffs.
18. As a maintainer, I want digest and reading-shell styles to stay one shared contract, so that Markdown/HTML membership and reading chrome cannot diverge on “which week.”
19. As a maintainer, I want ADR-aligned modules preserved (pipeline / week package / reading surface as adapter), so that responsive work stays CSS/HTML generation polish.
20. As a reader, I want no requirement for a local web server beyond opening files, so that `file://` still works.
21. As a reader, I want reduced-motion / calm layout (no flashy responsive animations), so that presence stays readable.
22. As a future trainer, I want past weeks still reachable from the list on a phone, so that teaching prep works on the go.
23. As an operator, I want README guidance that the reading entry is meant for desktop and mobile skim, so that I know the intended use.
24. As a careful reader, I want Traditional Chinese copy unchanged by the responsive pass, so that meaning is not reflow-edited.
25. As a maintainer, I want custom week ids still listed and selectable after layout changes, so that catch-up windows remain first-class.

## Implementation Decisions

- Prefer polishing the existing reading surface and digest HTML generation over introducing a new UI framework or hosted app.
- Primary test seam remains **`build_reading_surface`** (frozen today, multi-week fixtures): assert viewport meta, narrow-layout cues for the week list vs body, and digest body readability clues (brand image reference, overview/pillars/cards/appendix cues as already established).
- Per-week digest HTML continues to share the same stylesheet / generation path as the embedded digest body; do not add a second editorial or layout system.
- Target behavior (approved in product conversation): basic responsive—not a full multi-breakpoint design system; no requirement for a dedicated tablet-only layout beyond comfortable narrow stacking.
- CLI/pipeline already rebuilds the reading surface on finalize / rebuild-reading; this feature does not change editorial selection rules.
- Optional README note that the reading entry is intended for laptop reading and phone skim.

## Testing Decisions

- Good tests assert external behavior of generated HTML at `build_reading_surface`: viewport, presence of responsive layout cues for narrow viewports, week list + default/empty behavior still intact, brand and body clues present.
- Do not require Playwright/Selenium or visual screenshot regression for v1 of this polish.
- Prefer temporary fixture week packages (same style as existing reading-surface tests).
- Avoid asserting only private CSS class names unless those names encode the user-visible contract.

## Out of Scope

- Hosted website, PWA, native apps
- Full design system, dark mode productization, complex animation
- Browser automation / visual diff CI
- Changing selection, candidates, or finalize editorial rules
- Pixel-perfect print layout across browsers
- Separate tablet-only information architecture

## Further Notes

- Confirmed direction: current basic responsive approach is acceptable; formalize and lock rather than rebuild.
- Domain vocabulary: Digest, Week package, Reading surface, Week-stage pipeline (see project glossary).
- Parent effort is a follow-on to digest-reading-surface; keep that feature’s closed tickets untouched.

## Comments

- Seam agreed: `build_reading_surface` only; shared digest styles, no second seam.
- Ticket plan: single vertical slice (contract + light polish + brief docs).
