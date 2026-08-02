# Dedup store stays an independent module

Status: accepted

Weekly URL history (`seen_urls`) is a real concept, but we only have one file-backed adapter today. Absorbing dedup into the week-stage pipeline or into fetch would hide policy and make a future second store (e.g. in-memory for tests, or another persistence) a rewrite. The pipeline **orchestrates** `filter_duplicates` / `remember_items`; it does not own them. Promote a swappable history seam only when a second adapter actually appears (“one adapter = hypothetical seam, two = real”).

## Considered options

- **Pipeline owns history end-to-end** — rejected: mixes stage orchestration with persistence policy.
- **Fetch module absorbs dedup** — rejected: fetch becomes a grab-bag; hard to test history alone.
- **Independent dedup module (chosen)** — pipeline calls it; policy order documented at the pipeline layer.
