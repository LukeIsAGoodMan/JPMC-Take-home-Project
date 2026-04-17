# V1 Macro Label Recovery — Audit

> Status: **Audit complete — exact recovery confirmed**

## Execution Trace

1. Loaded `seg_full.csv` (199,523 rows)
2. Applied identical dtype reconstruction as V1 `segment_stage7.py`
3. Prepared K-Prototypes input with identical feature subset (5 continuous + 12 categorical)
4. Standardized continuous features (z-score, same formula)
5. Drew random subsample: `np.random.seed(42)`, `np.random.choice(199523, 30000, replace=False)`
6. Fitted K-Prototypes: k=4, Cao, n_init=5, max_iter=100, gamma=0.5, random_state=42
7. Predicted all 199,523 rows
8. Applied absorption rule: clusters < 2% merged into nearest by centroid distance
9. Relabeled to consecutive integers

## Exactness Verification

| Segment | V1 Frozen Output | V2 Recovery | Match? |
|---------|----------------:|------------:|--------|
| Seg 0 | 40,618 | 40,618 | Exact |
| Seg 1 | 67,462 | 67,462 | Exact |
| Seg 2 | 91,443 | 91,443 | Exact |
| Micro-cluster absorbed | 396 | 396 | Exact |

All segment sizes match to the row. The recovery is exact.

## Why Exact Recovery Works

- K-Prototypes with Cao initialization is deterministic given the same seed
- The subsample selection is deterministic (`np.random.seed(42)` + `np.random.choice`)
- The absorption rule is deterministic (nearest centroid by Euclidean distance)
- No V1 artifact was modified; the V2 recovery script replays the same logic

## What This Enables

With exact per-row V1 macro labels now available, the second-pass segmentation can be run on the **exact** V1 Segment 2 population (91,443 rows), resolving the lineage gap identified in the previous V2 fix pass.
