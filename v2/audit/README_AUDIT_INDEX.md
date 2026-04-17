# V2 Audit Index

## What This Is

This folder provides navigation and traceability for the V2 Decision-Driven Upgrade to the JPMC take-home ML project. V2 is an additive extension on top of the frozen V1 baseline.

## Where to Start

| Priority | File | Location |
|----------|------|----------|
| 1 | Final acceptance note | `v2/V2_FINAL_ACCEPTANCE_NOTE.md` |
| 2 | Visual report | `v2/V2_REPORT.html` or `.pdf` |
| 3 | Status summary | `v2/V2_SUMMARY.md` |
| 4 | This audit index | You are here |

## Folder Structure

```
v2/
  README_V2.md                     <- V2 overview
  V2_SUMMARY.md                    <- Full status tracker
  V2_FINAL_ACCEPTANCE_NOTE.md      <- Final accepted architecture
  V2_REPORT.html / .pdf            <- Polished final report

  audit/                           <- Navigation + traceability (this folder)
  design/                          <- Design artifacts (target, policy, segmentation)
  empirical/                       <- Evidence documents (score bands, benchmarks, robustness)
  segmentation/                    <- Layer 2 lineage, profiles, adoption decision
  decisions/                       <- Adoption decisions + change log
  results/                         <- Raw JSON/CSV data artifacts
  scripts/                         <- V2-side computation scripts
  archive/superseded/              <- Predecessor files no longer canonical
```

## Where to Find Key Evidence

| Claim | Primary Document | Supporting Data |
|-------|-----------------|----------------|
| CatBoost retained over LightGBM/XGBoost | `empirical/classifier_v2_benchmark.md` | `results/v2_phase4_results.json` |
| Weighted training not adopted | `empirical/weighted_training_experiments.md` | `results/v2_phase4_results.json` |
| Layer 2 conditionally adopted | `segmentation/segment2_exact_adoption_decision.md` | `results/segment2_exact_results.json` |
| V1 macro labels exactly recovered | `segmentation/v1_macro_label_recovery.md` | `results/v2_phase3_results.json`, `segmentation/v1_macro_labels.csv` |
| Score bands empirical | `empirical/score_band_analysis.md` | `results/v2_compute_results.json` |
| Multi-seed stability | `empirical/robustness_v2.md` | `results/v2_phase3_results.json` |
| Classifier quality by segment | `empirical/segment_conditioned_model_diagnostics.md` | Rules-based approx on val set |
| Fairness governance | `empirical/fairness_governance_note.md` | N/A (governance artifact) |

## Audit Sub-Documents

| File | Purpose |
|------|---------|
| `audit_documentation_map.md` | Maps each V2 claim to evidence |
| `final_artifact_manifest.md` | Lists all canonical final files |
| `accepted_vs_exploratory_map.md` | Status classification for every artifact |
| `file_lineage_map.md` | Supersession / predecessor tracking |
| `reviewer_reading_order.md` | Recommended reading sequence |
