# V2 Status Summary

## Overall Status: Phase 4 Complete — All Extensions Tested, Final Package Delivered

## Frozen V1 Baseline (unchanged)
| Component | Status |
|-----------|--------|
| Classifier (CatBoost, d=6/lr=0.08/l2=1.0, PR-AUC=0.70) | Frozen |
| Threshold policy (0.45/0.25/0.20) | Frozen |
| Macro segmentation (3 segments) | Frozen |
| All V1 pipeline/ and top-level docs | Frozen |

## V2 Artifact Status

### Workstream A — Target Design (Complete)
| File | Type |
|------|------|
| target_design_v2.md | Design |
| business_objective_hierarchy.md | Design |
| proxy_target_upgrade_options.md | Design |

### Workstream B — Decision Engine (Complete)
| File | Type |
|------|------|
| score_band_analysis.md | **Empirical** (canonical: v2_compute_results.json) |
| decision_policy_v2.md | Design + empirical |
| decision_policy_capacity_budget_framework.md | Empirical + assumed economics |

### Workstream C — Segmentation V2 (Complete)
| File | Type |
|------|------|
| v1_macro_label_recovery.md | **Empirical** — exact recovery confirmed |
| v1_macro_label_recovery_audit.md | Audit |
| v1_macro_labels.csv | **Empirical** artifact (199,523 rows) |
| segment2_exact_second_pass_design.md | Execution record |
| segment2_exact_profiles.md | **Conditionally adopted** empirical result |
| segment2_exact_profiles.html | **Conditionally adopted** empirical result |
| segment2_exact_results.json | Raw data |
| segment2_exact_adoption_decision.md | **Governance decision** |
| segmentation_v2_macro_micro_blueprint.md | Design (references exploratory predecessor) |
| segmentation_feature_scorecard.md | Design |
| exploratory_vs_operational_segmentation.md | Design |
| segment2_profiles.md | Superseded by exact version |
| segment2_profiles.html | Superseded by exact version |

### Workstream D — Integration (Complete)
| File | Type |
|------|------|
| score_segment_operating_matrix.md | Design |
| campaign_playbook_v2.md | Design |
| incremental_value_of_two_layer_design.md | Design |

### Workstream E — Robustness / Governance (Complete)
| File | Type |
|------|------|
| segment_conditioned_model_diagnostics.md | **Empirical** (rules-based macro assignment on val set, not exact V1 labels) |
| robustness_v2.md | **Empirical** (multi-seed) |
| fairness_governance_note.md | Governance |
| v1_to_v2_change_log.md | Traceability |
| second_pass_lineage_note.md | Governance (predecessor) |

### Workstream F — Packaging
| File | Type |
|------|------|
| README_V2.md | Planning doc |
| V2_SUMMARY.md | This file |

### Phase 4 — Optional Extensions (Complete)
| File | Type |
|------|------|
| weighted_training_experiments.md | **Tested, not adopted** |
| classifier_v2_benchmark.md | **Tested, CatBoost retained** |
| phase4_optional_extension_decision.md | Governance decision |
| V2_REPORT.html | Final V2 report |
| V2_FINAL_ACCEPTANCE_NOTE.md | Final acceptance |
| v2_phase4_experiments.py | Computation script |
| v2_phase4_results.json | Raw data |

## Key Phase 3 Findings

1. **V1 macro labels exactly recovered** — verified to match frozen V1 output (40,618 / 67,462 / 91,443)
2. **Layer 2: 3 sub-segments on exact V1 Segment 2** — Established Earners (38%, 20.7% >50K), Service Workers (11%, 2.4%), Younger Workers (51%, 8.6%)
3. **Multi-seed stability**: 3/4 seeds produce 3 sub-segments; service-worker group is most stable
4. **Adoption decision**: Conditionally adopted — exact lineage, meaningful differentiation, acknowledged stability caveat
5. **Classifier PR-AUC by segment** (rules-based macro assignment): 0.70 (working-age), 0.57 (seniors) — score trustworthiness is segment-dependent
