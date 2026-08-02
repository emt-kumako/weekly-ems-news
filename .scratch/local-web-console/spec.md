Status: ready-for-agent
Type: spec
Feature: local-web-console

# Local web console — Spec

## Problem Statement

I already have a week-stage pipeline (fetch → draft → candidates → finalize) and an HTML reading surface, but operating it still means remembering CLI commands and editing Markdown in an editor. I want a local browser console on my machine so I can run the full weekly workflow and read the digest without using the terminal for routine steps—and without hosting a public website.

## Solution

Add a **local-only web console** (loopback server) that wraps the existing pipeline and week package: pick a week, fetch, draft, tick candidates in the browser, finalize, and open/refresh the reading surface. The CLI remains available; the console is another thin adapter. No cloud deploy, no accounts.

## User Stories

1. As an editor, I want to start a local console with one command, so that I can work from the browser.
2. As an editor, I want the server bound to localhost only, so that my week packages are not exposed on the LAN by default.
3. As an editor, I want to see today’s ISO week as the default week, so that I land on the current cycle.
4. As an editor, I want to pick or enter another week id (including custom catch-up ids), so that I can work on non-default weeks.
5. As an editor, I want to run fetch from the console (with an offline option), so that I do not need the terminal for intake.
6. As an editor, I want to run draft from the console, so that candidates.md is produced without CLI.
7. As an editor, I want to see candidate items with checkboxes, so that I can select what enters the digest.
8. As an editor, I want to edit the week tagline in the console, so that finalize picks up the masthead line.
9. As an editor, I want to save candidate selections back to the week package, so that disk state stays the source of truth.
10. As an editor, I want to finalize from the console, so that digest.md, digest.html, and the reading index update.
11. As a reader, I want a link or embedded view of the reading surface after finalize, so that I can verify the week immediately.
12. As an operator, I want rebuild-reading available in the console, so that layout refreshes need no refetch.
13. As an operator, I want clear success/error messages for each action, so that I know what failed.
14. As a maintainer, I want the console to call existing pipeline/week-package seams, so that selection rules are not reimplemented in the UI.
15. As a maintainer, I want a testable service seam above HTTP, so that CI does not need a real browser.
16. As an operator, I want README instructions for `serve` and the localhost URL, so that I can find the console.
17. As an editor, I want status cues (has items / candidates / digest), so that I know which step is next.
18. As a careful operator, I want Traditional Chinese UI labels where the product is Chinese-first, so that the console matches the digest language.

## Implementation Decisions

- Local HTTP server on 127.0.0.1; CLI command such as `serve`.
- Console is an adapter over `run_fetch` / `run_draft` / `run_finalize` / `run_rebuild_reading_surface` and week-package candidate load/save—not a second editorial engine.
- Primary test seam: console service functions (status, save selection, run stages) with tmp_path fixtures; HTTP wiring stays thin.
- Prefer stdlib HTTP if practical to avoid heavy new dependencies; static console HTML/JS served by the same process.
- Reading surface remains generated files; console links to or serves them locally after rebuild/finalize.

## Testing Decisions

- Assert external behavior at the console service seam: week status flags, candidate selection persistence, finalize producing digest + reading index, fetch/draft offline paths where fixtures allow.
- No Playwright requirement for v1.
- Prior art: pipeline and reading_surface fixture tests.

## Out of Scope

- Public/hosted deployment, auth, multi-user
- Replacing Markdown candidates as the on-disk format
- Native mobile/desktop app packaging (Tauri/Electron)
- Live collaborative editing

## Further Notes

- Product choice: Option A (local web) + scope 3 (full week workflow).
- Respect ADR week-stage pipeline / week-package / assemble shape.
