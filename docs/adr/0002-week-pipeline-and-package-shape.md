# Week-stage pipeline, week package, and assemble entry points

Status: accepted

Deepening after the architecture review:

1. **Week-stage pipeline** exposes exactly three operations: `run_fetch`, `run_draft`, `run_finalize`. The CLI is an adapter (paths / week id only).
2. **Week package** owns on-disk round-trips with a small interface: `load_items`, `write_candidates`, `finalize`. Finalize logic (parse candidates → assemble → write digest) lives here, not in the pipeline. Fixture JSON and `items.json` share one codec.
3. **Draft** content comes from the drafting module; the package only writes candidates. **Fetch** stays thin orchestration: transport → dedup → package write → remember.
4. **Assemble week** is the digest seam, with two named entry points: `assemble_week_auto` and `assemble_week_from_candidates`. Merge / select / render stay inside that implementation.
5. **Source transport** adapters return raw `title + excerpt + url + fetched_at`. Normalizing into NewsItem stays in the fetch module. Fixture and HTTP are the two adapters that justify the seam.

LLM chat injection remains optional / speculative and is not required for this shape.
