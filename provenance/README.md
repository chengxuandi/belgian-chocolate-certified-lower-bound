# Provenance archive

This directory separates raw discovery provenance from the finite certificate.
The raw method record is intentionally preserved byte-for-byte.

## Original record

- Source path: `D:\ai4sc\gbcp-certified-lower-bound-github\supplementary\project_METHOD.md`
- Published copy: [`ORIGINAL_AGENT_METHOD_LOG.md`](ORIGINAL_AGENT_METHOD_LOG.md)
- Copy timestamp: `2026-09-15T22:49:22.8982399+08:00`
- Source Git commit at copy: `7f2283a96641078d6ccb2abf04468866a3d8a52a`
- SHA-256: `9c064592cfd6e5563de85378866f4960ed175e23c27fd69b98125a373840cc79`

This is the contemporaneous research-process record, not a retrospective
paper narrative. It retains the recorded search ranges, failures, fallbacks,
and stopping-audit corrections.

## Review records

`reviews/` contains compact JSON records selected from the working search
directory: scaled Newton and fast-Jacobian reviews, residual-only and mpmath
backend reviews, adjacency coverage, parent-growth fallback, circuit and
parallel-check reviews, precision review, and adversarial checker mutations.

The larger frozen frontier state and search archive remain under
[`../supplementary/`](../supplementary/), especially:

- `project_state.json`;
- `search_archive.zip`;
- `primary_clean_check.log` and `audit_clean_check.log`;
- source interval and witness records.

## Reading rule

These files explain discovery and verification history. They do not replace
the exact certificate. For the theorem, use the root-level witness and the two
independent standard-library verifiers.
