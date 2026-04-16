# Segmentation Design

> Derived from: pipeline/outputs/stage7/SEGMENTATION_METHOD_SELECTION.md, SEGMENTATION_REPORT.md, TECHNICAL_APPENDIX.md

## Why Segmentation Exists Beyond the Classifier

The classifier tells you *who is likely high-income*. It does not tell you *who these people are* or *how to approach them*. Segmentation provides the action-design layer: it groups people by life-stage, employment, and household patterns so the business can differentiate messaging, products, and channels.

## Why K-Prototypes

The dataset has 24 categorical and 7 numeric features. K-Prototypes handles mixed-type data natively using Euclidean distance for numerics and Hamming distance for categoricals. This avoids the information loss of one-hot encoding that K-Means would require.

Gamma was set to 0.5 to reduce the dominance of categorical features (12 of 17 clustering inputs are categorical).

## Feature Subset

17 features selected for clustering (5 continuous + 12 categorical), focused on life-stage, employment, and household dimensions. High-cardinality codes (detailed industry/occupation recode, country of birth) excluded to reduce noise.

**Continuous**: age, weeks worked in year, capital gains, dividends from stocks, wage per hour

**Categorical**: education, marital stat, sex, major occupation code, major industry code, full or part time employment stat, tax filer stat, detailed household summary in household, family members under 18, class of worker, citizenship, own business or self employed

## Subsample Strategy

K-Prototypes was fit on a **random subsample** of 30,000 rows (seed=42). Random sampling is appropriate because the CPS dataset has no temporal ordering to preserve. Full dataset (199,523 rows) was assigned using the fitted model's predict method.

## k Evaluation and Final Segment Count

| k | Cost | Smallest Cluster | Viable? |
|---|-----:|------------------:|---------|
| 3 | 160,818 | 20.4% | Yes |
| 4 | 127,683 | 0.2% | No |
| 5 | 109,444 | 0.2% | No |
| 6 | 104,174 | 0.1% | No |
| 7 | 88,091 | 0.2% | No |
| 8 | 83,082 | 0.2% | No |

In the evaluation outputs, k=3 is stable while k>=4 consistently produces micro-clusters (0.1-0.2%).

**Final approach**: Request k=4 to separate the 3 macro-groups from the outlier explicitly. Apply a deterministic absorption rule: any cluster smaller than 2% of data is merged into its nearest neighbor by continuous-feature centroid distance.

**Final business deliverable: 3 segments.**

The k=4 request is an intermediate modeling step, not the final segment count. The absorption rule is documented and reproducible.

## Target and Weight Exclusion

- `_target` (income label): **excluded from clustering input**. Used only after clustering for profiling and enrichment calculation.
- `_weight` (CPS survey weight): **excluded from clustering input**. Used only for population-level segment sizing.

## Final 3 Segments

| Seg | Name | Wtd Share | >50K Rate | Enrichment |
|-----|------|----------|-----------|------------|
| 0 | Senior/Retired Householders | 20.1% | 2.2% | 0.35x |
| 1 | Youth/Dependent Non-Workforce | 33.1% | 0.05% | 0.01x |
| 2 | Mid-Career Working Householders | 46.7% | 12.5% | 2.12x |

## Segment Actionability

- **Segment 0**: Retirement products, estate planning, Medicare supplements
- **Segment 1**: Family-indirect marketing, youth savings, education products
- **Segment 2**: Premium financial products, investment, wealth management

The segmentation converts the classifier's score into differentiated marketing action.
