# File Lineage Map

Tracks which files superseded earlier versions.

## Supersession Chain

| Predecessor (archive/superseded/) | Replaced By (canonical) | Reason |
|----------------------------------|------------------------|--------|
| `segment2_profiles.md` | `segmentation/segment2_exact_profiles.md` | Rules-based approx → exact V1 lineage |
| `segment2_profiles.html` | `segmentation/segment2_exact_profiles.html` | Same |
| `segment2_second_pass_design.md` | `segmentation/segment2_exact_second_pass_design.md` | Execution plan → execution record on exact population |
| `segmentation_v2_results.json` | `results/segment2_exact_results.json` | Approximate → exact data |

## Files That Were Patched In Place (not superseded, just corrected)

| File | Fix | Phase |
|------|-----|-------|
| `decision_policy_v2.md` | Estimated tables → empirical; status updated | Phase 2 fix |
| `decision_policy_capacity_budget_framework.md` | Stale estimates → canonical JSON numbers | Phase 2 fix |
| `score_band_analysis.md` | top-100/500 numbers aligned to canonical JSON | Phase 2 final fix |
| `campaign_playbook_v2.md` | Hypothetical micro-segments → actual exploratory findings | Phase 2 fix |
| `segment_conditioned_model_diagnostics.md` | Added rules-based approx caveat | Phase 3 fix |

## Canonical Source of Truth for Numbers

`results/v2_compute_results.json` — score bands, cumulative capture, all empirical tables
`results/v2_phase3_results.json` — V1 label recovery, exact second-pass, multi-seed stability
`results/v2_phase4_results.json` — weighted training, benchmark
