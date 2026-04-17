# V1 to V2 Change Log

## V1 (Frozen Baseline)

| Component | V1 Deliverable |
|-----------|---------------|
| Classifier | CatBoost, reduced features, d=6/lr=0.08/l2=1.0, PR-AUC=0.70 |
| Threshold | 3 fixed modes (0.45/0.25/0.20) |
| Segmentation | 3 macro life-stage segments (seniors/youth/working-age) |
| Framing | Two-layer targeting design |

## What V2 Added

### Accepted / Adopted

| Addition | Status | Evidence |
|----------|--------|---------|
| Target hierarchy (Tier 0-3) | Design artifact | Documents proxy → production target path |
| Score-band analysis | Empirical | Real score distributions and cumulative capture |
| Budget/capacity decision framework | Design + empirical | Budget-to-outcome table from model |
| V1 macro label exact recovery | Empirical | Verified to match V1 frozen output |
| Layer 2: 3 working-age sub-segments | **Conditionally adopted** | Exact V1 lineage; 3/4 seed stability |
| Segment-conditioned diagnostics | Empirical (rules-based macro assignment on val set) | PR-AUC by macro segment; not exact V1 labels |
| Fairness governance note | Governance artifact | Documents demographic feature sensitivity |

### Exploratory / Informational

| Addition | Status | Notes |
|----------|--------|-------|
| Previous rules-based second-pass | Superseded | Replaced by exact-lineage version |
| Proxy target upgrade options | Design only | Tier 1 candidates described, not built |
| Campaign playbook scenarios | Design | Uses assumed economics, clearly labeled |

### Not Started / Deferred

| Item | Reason |
|------|--------|
| Weighted-training experiments | Lower priority than lineage repair |
| LightGBM/XGBoost benchmark | Lower priority |
| Exploratory broad-feature segmentation track | Operational track completed first |
| V2 final HTML report | Deferred until all V2 content is stable |

## Phase 4: Optional Extensions (tested, not adopted)

| Extension | Result | Decision |
|-----------|--------|----------|
| Weighted training (3 variants) | All underperformed baseline by 0.004-0.006 PR-AUC | Not adopted |
| LightGBM benchmark | PR-AUC 0.6839 (-0.009 vs CatBoost) | Not adopted |
| XGBoost benchmark | PR-AUC 0.6829 (-0.010 vs CatBoost) | Not adopted |

These experiments confirm the accepted V2 baseline rather than challenging it.

## Key V2 Insights Beyond V1

1. **Score-band analysis** reveals 81% of population in Band E (< 0.05) — the model's value concentrates in the top 6% of scored individuals
2. **Layer 2 sub-segments** show a 9x income-rate difference within working-age (20.7% vs 2.4%) — the macro segment was hiding significant internal heterogeneity
3. **Classifier quality varies by segment**: PR-AUC 0.70 in working-age but only 0.57 in seniors — score interpretation should be segment-aware
4. **The service-worker sub-segment** (~11% of working-age) is the most stable Layer 2 finding across seeds
5. **CatBoost's native categorical handling** is a structural advantage: LightGBM and XGBoost both underperform by ~0.01 PR-AUC on this high-categorical dataset
6. **Survey-weighted training hurts**: all weight variants degrade performance, confirming the V1 governance decision
