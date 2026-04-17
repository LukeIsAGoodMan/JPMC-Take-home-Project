# V1 Macro Label Recovery

> Status: **Completed — exact recovery successful**

## Method

Re-ran the frozen V1 segmentation logic exactly:
- K-Prototypes, k=4, Cao init, n_init=5, max_iter=100, gamma=0.5, seed=42
- Random subsample of 30,000 rows (same seed → same subsample)
- Predicted all 199,523 rows
- Absorbed micro-clusters (<2%) into nearest neighbor

## Result

| V1 Macro Segment | Rows | % | >50K Rate |
|-----------------|-----:|--:|----------:|
| Seg 0: Senior/Retired | 40,618 | 20.4% | 2.23% |
| Seg 1: Youth/Dependent | 67,462 | 33.8% | 0.05% |
| Seg 2: Working-Age | 91,443 | 45.8% | 12.51% |

These match the frozen V1 segment profiles exactly (V1 reported 40,618 / 67,462 / 91,443).

## Verification

The recovered segment sizes are identical to V1's `stage7_results.json` profiles, confirming that the replay is exact — same subsample, same initialization, same absorption.

## Artifact

Per-row labels saved to: `v2/v1_macro_labels.csv` (199,523 rows, column `v1_macro_segment`).

This file is a V2-side artifact. No V1 files were modified.
