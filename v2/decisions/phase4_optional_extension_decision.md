# Phase 4 Optional Extension Decisions

> Status: **Decisions finalized**

## Summary

| Extension | Result | Decision |
|-----------|--------|----------|
| Weighted training (normalized) | PR-AUC 0.6896 (-0.0036 vs baseline) | **Not adopted** |
| Weighted training (sqrt) | PR-AUC 0.6887 (-0.0045 vs baseline) | **Not adopted** |
| Weighted training (capped p99) | PR-AUC 0.6876 (-0.0056 vs baseline) | **Not adopted** |
| LightGBM benchmark | PR-AUC 0.6839 (-0.0093 vs baseline) | **Tested, not adopted** |
| XGBoost benchmark | PR-AUC 0.6829 (-0.0103 vs baseline) | **Tested, not adopted** |

## Accepted V2 Classifier Baseline After Phase 4

**Unchanged.** The accepted baseline remains:

- **Model**: CatBoost
- **Features**: Reduced set (31 features, 5 sparse review columns removed)
- **Params**: depth=6, learning_rate=0.08, l2_leaf_reg=1.0
- **Training weights**: None (unweighted training)
- **Test PR-AUC**: 0.7008
- **Threshold**: 0.25 balanced / 0.45 precision / 0.20 recall

No optional extension improved on this baseline. The experiments confirm rather than challenge the accepted architecture.
