# Selected search material

This directory contains a small, reviewable subset of the search code and
intermediate records. It is not an exhaustive dump of the multi-gigabyte
working directory.

- `frontier_search.py` and `complete_adjacency.py` implement the recorded
  configuration frontier and coverage pass.
- `origin_backfill.py` records the origin-growth backfill path.
- `review_fast_mp.py`, `review_residual_only.py`, and
  `review_mpmath_backend.py` are review scripts for numerical discovery
  accelerations.
- The JSON files record the corresponding review outcomes, including the
  parent-growth fallback and adjacency coverage.

The full frozen state and compressed search archive are retained one level up
in `supplementary/project_state.json` and `supplementary/search_archive.zip`.
Numerical search is discovery material only; it is not needed to prove the
published lower bound.
