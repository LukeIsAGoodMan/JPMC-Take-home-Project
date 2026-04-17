# Robustness Assessment — V2

> Status: **Empirical result**

## Multi-Seed Stability of Layer 2 Sub-Segments

The exact second-pass segmentation (on V1 Segment 2, 91,443 rows) was run across 4 seeds:

| Seed | Final k | Segment Sizes | Stable? |
|------|--------:|--------------|---------|
| 42 (primary) | 3 | 34,904 / 10,239 / 46,300 | Primary result |
| 52 | 3 | 73,196 / 11,010 / 7,237 | 3 segments, different proportions |
| 62 | 3 | 47,069 / 34,120 / 10,254 | 3 segments, different proportions |
| 72 | 2 | 79,447 / 11,996 | Only 2 segments |

### Assessment

- **3-segment structure**: Appears in 3 of 4 seeds. Partially stable.
- **~10K low-income service-worker group**: Present at every seed (10K-12K rows). **Most stable finding.**
- **Established vs younger worker split**: Varies significantly in relative size across seeds. This boundary is soft.
- **2-segment fallback**: At seed=72, the two larger groups merge, leaving only the service-worker split.

### Conclusion

The Layer 2 segmentation is **conditionally stable**:
- The service-worker sub-segment is robust
- The 3-way split is the majority outcome but not guaranteed
- Sub-segment boundaries should be treated as directional

This is expected for K-Prototypes on census data with many categorical features. The segmentation provides useful group-level structure but should not be interpreted as having precise, fixed boundaries.

## Year-Level Classifier Stability (from V1 Stage 6)

| Year | PR-AUC | F1 |
|------|--------|----|
| 94 | 0.6817 | 0.622 |
| 95 | 0.7038 | 0.637 |

Minor temporal variation, no instability concern.

## What Multi-Seed Testing Does NOT Cover

- Does not test feature-selection robustness (only seed varies, not features)
- Does not test K-Prototypes vs alternative methods
- Does not test sensitivity to gamma parameter
- Does not assess whether subsample size (20K) is sufficient

These would be appropriate for a production validation but exceed the scope of a take-home exercise.
