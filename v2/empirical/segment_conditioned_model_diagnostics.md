# Segment-Conditioned Classifier Diagnostics

> Status: **Empirical result with approximate macro assignment**
>
> **Lineage caveat**: The macro segment labels on the validation set are a **rules-based approximation** (age/education/employment rules), not exact V1 K-Prototypes labels. Exact V1 labels were recovered for `seg_full.csv` but were not row-mapped onto the classifier validation split in this pass. The diagnostics are directionally useful but are not exact V1-label-conditioned results.

## Objective

How does the V1 classifier perform within each macro segment? Where is the score more vs less trustworthy?

## Metrics by Macro Segment (validation set, threshold=0.25, rules-based segment assignment)

| Segment | N | Positives | PR-AUC | ROC-AUC | F1 | Brier |
|---------|----:|--------:|-------:|--------:|---:|------:|
| Senior/Retired | 4,024 | 84 | 0.5732 | 0.9183 | 0.5352 | — |
| Youth/Dependent | 8,422 | 0 | — | — | — | — |
| Working-Age | 17,483 | 1,773 | 0.6989 | 0.9277 | 0.6334 | — |

*Youth/Dependent has zero positives in the validation set — metrics are not computable. This is expected: the segment has a 0.05% base rate.*

## Key Findings

### 1. Classifier quality varies significantly by segment

- **Working-Age**: PR-AUC 0.70, F1 0.63 — strong. This is where most of the model's value concentrates.
- **Senior/Retired**: PR-AUC 0.57, F1 0.54 — weaker. Low base rate (2.1% in val) makes classification harder. The model can still rank within this segment, but at lower discrimination.
- **Youth/Dependent**: Not applicable — essentially zero positives.

### 2. Score interpretation should be segment-aware

A score of 0.30 means different things in different segments:
- In Working-Age: reasonably confident signal (base rate 10%+)
- In Senior/Retired: weaker signal (base rate 2%; the model is less calibrated here)
- In Youth: meaningless (near-zero positive rate regardless of score)

### 3. Threshold policy should be segment-conditional

The current uniform threshold (0.25) may be suboptimal per segment:
- **Working-Age**: threshold 0.25 is well-supported (PR-AUC 0.70)
- **Senior/Retired**: a higher threshold (0.40+) is appropriate to compensate for lower discrimination
- **Youth/Dependent**: exclude entirely from income-based targeting

### 4. Implications for Layer 2

Within the working-age segment, the 3 sub-segments have different >50K base rates (20.7%, 2.4%, 8.6%). The classifier's within-segment ranking quality may also differ:
- **Established Earners** (20.7% base): richest signal, most true positives to find
- **Service Workers** (2.4% base): very low rate — similar to seniors in targeting difficulty
- **Younger Workers** (8.6% base): moderate — classifier score is the main differentiation tool here

## Recommendation

Present the classifier score with segment context. A campaign manager should know not just the score but which macro/micro segment the individual belongs to, because score reliability varies.
