# Audit Documentation Map

Maps each major V2 claim to its supporting evidence.

| # | Claim | Primary Document | Raw Data |
|---|-------|-----------------|----------|
| 1 | CatBoost is the best classifier | `empirical/classifier_v2_benchmark.md` | `results/v2_phase4_results.json` |
| 2 | Weighted training degrades performance | `empirical/weighted_training_experiments.md` | `results/v2_phase4_results.json` |
| 3 | Score bands: 81% in Band E, budget knee at 1500-2000 | `empirical/score_band_analysis.md` | `results/v2_compute_results.json` |
| 4 | V1 macro labels exactly recovered (40,618/67,462/91,443) | `segmentation/v1_macro_label_recovery.md` + `_audit.md` | `segmentation/v1_macro_labels.csv` |
| 5 | Layer 2: 3 sub-segments on exact V1 Seg 2 | `segmentation/segment2_exact_profiles.md` | `results/segment2_exact_results.json` |
| 6 | Layer 2 conditionally adopted | `segmentation/segment2_exact_adoption_decision.md` | Multi-seed in `results/v2_phase3_results.json` |
| 7 | Multi-seed stability: 3/4 seeds → 3 sub-segments | `empirical/robustness_v2.md` | `results/v2_phase3_results.json` |
| 8 | Classifier PR-AUC varies by segment (0.70 vs 0.57) | `empirical/segment_conditioned_model_diagnostics.md` | Rules-based approx (caveat documented) |
| 9 | Target hierarchy: Tier 0-3 | `design/target_design_v2.md` + `design/business_objective_hierarchy.md` | Design artifact (no raw data) |
| 10 | 9x income differential within working-age | `segmentation/segment2_exact_profiles.md` | 20.7% vs 2.4% from profiles |
