# Preprocessing Plan

> Derived from: pipeline/outputs/PREPROCESSING_AUDIT.md, pipeline/outputs/column_treatment.md, TECHNICAL_APPENDIX.md

## Target Handling

| Raw Value | Mapped | Notes |
|-----------|--------|-------|
| `- 50000.` | 0 | <= $50K |
| `50000+.` | 1 | > $50K |

Target is excluded from all feature matrices. Used only as label for classification and ex-post profiling for segmentation.

## Weight Handling

- **Excluded from features** — never a predictor
- **Excluded from training sample weights** — survey weights address population representativeness, not label imbalance; CPS weights vary 500x and would destabilize optimization
- **Used in evaluation** — survey-weighted metrics for population-representative performance
- **Used in segmentation** — weighted segment sizing for population interpretation

## Missing / Exception / Sentinel Handling

| Category | Values | Treatment |
|----------|--------|-----------|
| Structural not-applicable | `Not in universe`, `Not in universe under 1 year old`, `Children or Armed Forces` | Preserved as explicit category |
| Unknown / ambiguous | `?` | Mapped to `Unknown` |
| True blank | (rare) | `Missing` in categoricals, NaN in numerics |
| Numeric zeros | 0 in financial columns | Preserved as valid values |

## Numeric-Coded Categorical Handling

| Column | Value Range | Action |
|--------|-------------|--------|
| detailed industry recode | 0-51 | Cast to string |
| detailed occupation recode | 0-46 | Cast to string |
| own business or self employed | 0-2 | Cast to string |
| veterans benefits | 0-2 | Cast to string |
| year | 94-95 | Cast to string |

These are semantic codes, not measurements. Casting to string prevents accidental mean/scaling.

## Split Strategy

| Split | Rows | % | Target Rate |
|-------|-----:|--:|------------|
| Train | 139,665 | 70% | 6.21% |
| Validation | 29,929 | 15% | 6.20% |
| Test | 29,929 | 15% | 6.20% |

- Stratified on target label
- Year distribution balanced (~50/50 in each split)
- All encoders/scalers fit on train only
- Seed: 42

## Classification vs Segmentation Data Preparation

| Aspect | Classification | Segmentation |
|--------|---------------|-------------|
| Dataset | Train/val/test splits | Full 199,523 rows |
| Features | 31 (reduced) + 4 log1p | 17 (focused life-stage subset) |
| Target | Used as label | Excluded from input; profiling only |
| Weight | Evaluation only | Segment sizing only |
| Sparse review cols | Excluded (5 columns) | Excluded (9 columns) |
| Supervised/unsupervised | Supervised | Unsupervised |
