# Weighted Training Experiments

> Status: **Tested, NOT adopted**

## Objective

Test whether using CPS survey weights during training improves the V2 accepted baseline.

## Variants Tested

All variants use the accepted CatBoost configuration (d=6, lr=0.08, l2=1.0) with different training sample weights:

| Variant | Weight Transform | Rationale |
|---------|-----------------|-----------|
| baseline (no weight) | None | Accepted V2 baseline |
| normalized | w / mean(w) | Scale weights to mean=1 |
| sqrt | sqrt(w / mean(w)) | Compress extreme weights |
| capped_p99 | clip(w, 99th pct) / mean | Cap extreme weights at 99th percentile |

## Results (validation, threshold=0.25)

| Variant | UW PR-AUC | UW F1 | SW PR-AUC | SW F1 |
|---------|----------|-------|----------|-------|
| **baseline (no weight)** | **0.6932** | **0.6299** | **0.6906** | — |
| normalized | 0.6896 | 0.6272 | 0.6881 | — |
| sqrt | 0.6887 | 0.6279 | 0.6859 | — |
| capped_p99 | 0.6876 | 0.6285 | 0.6860 | — |

## Decision: NOT ADOPTED

**Every weighted-training variant underperforms the unweighted baseline** on both unweighted and survey-weighted evaluation. The degradation is consistent (-0.003 to -0.006 PR-AUC) across all variants.

This confirms the V1 governance decision: CPS survey weights address population representativeness, not label imbalance. Using them as training sample weights distorts the optimization without compensating benefit. Survey-weighted evaluation (which the project already implements) is the correct use of these weights.
