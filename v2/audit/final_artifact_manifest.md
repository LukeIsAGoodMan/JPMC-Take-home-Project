# Final Artifact Manifest

Files a reviewer should treat as the accepted V2 package.

## Top-Level Final Deliverables
- `V2_FINAL_ACCEPTANCE_NOTE.md` — final accepted architecture
- `V2_REPORT.html` — polished visual report
- `V2_REPORT.pdf` — PDF version
- `V2_SUMMARY.md` — full status tracker
- `README_V2.md` — V2 overview and plan

## Accepted Design Artifacts (design/)
- `target_design_v2.md`
- `business_objective_hierarchy.md`
- `proxy_target_upgrade_options.md`
- `decision_policy_v2.md`
- `decision_policy_capacity_budget_framework.md`
- `segmentation_v2_macro_micro_blueprint.md`
- `segmentation_feature_scorecard.md`
- `score_segment_operating_matrix.md`
- `campaign_playbook_v2.md`
- `incremental_value_of_two_layer_design.md`
- `exploratory_vs_operational_segmentation.md`

## Accepted Empirical Evidence (empirical/)
- `score_band_analysis.md` — empirical
- `classifier_v2_benchmark.md` — tested, CatBoost retained
- `weighted_training_experiments.md` — tested, not adopted
- `robustness_v2.md` — multi-seed stability
- `segment_conditioned_model_diagnostics.md` — empirical (rules-based approx caveat)
- `fairness_governance_note.md` — governance

## Accepted Segmentation Materials (segmentation/)
- `v1_macro_label_recovery.md` + `_audit.md` — exact recovery
- `v1_macro_labels.csv` — 199,523-row labels
- `segment2_exact_second_pass_design.md`
- `segment2_exact_profiles.md` + `.html`
- `segment2_exact_adoption_decision.md`
- `second_pass_lineage_note.md`

## Decisions (decisions/)
- `phase4_optional_extension_decision.md`
- `v1_to_v2_change_log.md`

## Raw Support Data (results/)
- `v2_compute_results.json`
- `v2_phase3_results.json`
- `v2_phase4_results.json`
- `segment2_exact_results.json`
- `classifier_v2_results.json`

## Scripts (scripts/)
- `v1_label_recovery.py`
- `v2_compute.py`
- `v2_phase4_experiments.py`

## NOT Part of Final Package
- `archive/superseded/*` — predecessor files, kept for traceability only
- `catboost_info/` — CatBoost training cache, not a deliverable
