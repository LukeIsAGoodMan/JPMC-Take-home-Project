# V2 — Decision-Driven Upgrade

## What V2 Is

V2 is an additive upgrade on the frozen V1 project. V1 proved a sound two-layer methodology (classifier + segmentation). V2 pushes it toward a more commercially meaningful, decision-driven targeting system.

**V1 is frozen and preserved.** V2 does not alter V1 artifacts, metrics, or conclusions.

## V1 Baseline (Frozen)

| Aspect | V1 Conclusion |
|--------|--------------|
| Classifier | CatBoost, reduced features, depth=6, lr=0.08, l2=1.0 |
| Test PR-AUC | 0.7008 |
| Threshold | 0.25 balanced, 0.45 precision, 0.20 recall |
| Segmentation | 3 macro segments (seniors, youth, working-age) via K-Prototypes |
| Core insight | Two-layer targeting: score + segment + threshold policy |

## What V2 Changes

| Dimension | V1 | V2 Direction |
|-----------|-----|-------------|
| Target | Binary income >$50K only | Target hierarchy (proxy → upgraded → true business) |
| Threshold | 3 fixed operating modes | Budget/capacity-aware decision framework |
| Segmentation | 3 macro life-stage groups | Macro layer preserved + micro sub-segmentation within working-age |
| Integration | Classifier and segments described separately | Score x Segment operating matrix |
| Governance | Single-seed, single-model | Multi-seed robustness, segment-conditioned diagnostics |

## V2 Folder Structure

```
v2/
  README_V2.md                  <- this file
  V2_SUMMARY.md                 <- status tracker

  # Workstream A — Target Design
  target_design_v2.md
  business_objective_hierarchy.md
  proxy_target_upgrade_options.md

  # Workstream B — Decision Engine
  score_band_analysis.md
  decision_policy_v2.md
  weighted_training_experiments.md
  classifier_v2_benchmark.md

  # Workstream C — Segmentation V2
  segmentation_v2_macro_micro_blueprint.md
  segment2_second_pass_design.md
  exploratory_vs_operational_segmentation.md
  segmentation_feature_scorecard.md

  # Workstream D — Integration
  score_segment_operating_matrix.md
  campaign_playbook_v2.md
  incremental_value_of_two_layer_design.md

  # Workstream E — Robustness
  robustness_v2.md
  segment_conditioned_model_diagnostics.md
  fairness_governance_note.md
  v1_to_v2_change_log.md

  # Workstream F — Packaging
  (final V2 packaging docs, created last)
```

## Phased Execution Plan

### Phase 1 — Design Foundation (current)
- **Workstream A**: Target hierarchy design (design-only)
- **Workstream B**: Score-band analysis + decision policy (design + light computation)
- **Workstream C**: Macro/micro segmentation blueprint (design + second-pass plan)

### Phase 2 — Experiments
- **Workstream B**: Weighted-training experiments, optional benchmark expansion
- **Workstream C**: Second-pass clustering within working-age, exploratory branch
- **Workstream D**: Score x Segment integration matrix

### Phase 3 — Governance + Packaging
- **Workstream E**: Multi-seed robustness, fairness note, segment-conditioned diagnostics
- **Workstream F**: V2 packaging, change log, final summary

## Workstream Classification

| Workstream | Type | Computation | Priority |
|-----------|------|-------------|----------|
| A — Target design | Design-only | None | High (frames everything) |
| B — Score bands + policy | Design + light compute | Score-band stats from existing model | High |
| B — Weighted training | Experimental | Model retraining | Medium |
| C — Macro/micro blueprint | Design | None | High |
| C — Second-pass clustering | Experimental | New clustering run | Medium |
| D — Integration matrix | Design + synthesis | Light | Medium-High |
| E — Robustness | Experimental | Multi-seed runs | Lower |
| F — Packaging | Documentation | None | Last |

## Highest-Value First Task

**Workstream A (target design)** + **Workstream B (decision policy)** + **Workstream C (macro/micro blueprint)** — these three design documents frame everything else and require no new computation. They are the foundation for all Phase 2 experiments.
