# Client Report Draft

> Derived from: CLIENT_REPORT.md (blueprint-aligned copy)
>
> This is the blueprint-required "client_report_draft" artifact. The final client report is `CLIENT_REPORT.md` at the project root.

## Executive Summary

We built two complementary tools for retail targeting using CPS census data (199,523 individuals, 1994-1995):

1. **An income scoring model** that identifies individuals likely to earn more than $50,000. The model achieves strong discriminative performance (ROC-AUC 0.96, PR-AUC 0.70 on held-out test data) and can be tuned to different operating modes depending on the business use case.

2. **A population segmentation** that divides the population into 3 actionable groups based on life-stage, employment, and household patterns — each suggesting different marketing approaches.

Together, these form a **two-layer targeting design**: the classifier tells you *who to prioritize*, and the segmentation tells you *how to approach them*.

## The Business Problem

A retail client wants to identify high-income individuals for premium product targeting. Income above $50,000 serves as a proxy for purchasing power and product affinity.

**Important**: Income is a *proxy target*, not the ultimate business objective. The classifier should be treated as a prioritization and routing tool.

## How to Use the Classifier

The classifier outputs a probability (0-1). The business decision is what to do with that score:

| Mode | Threshold | Precision | Recall | Use Case |
|------|-----------|-----------|--------|----------|
| Precision-leaning | 0.45 | 73% | 51% | Expensive outreach — fewer contacts, higher hit rate |
| Balanced | 0.25 | 58% | 68% | General targeting — best overall tradeoff |
| Recall-leaning | 0.20 | 53% | 73% | Broad screening — cast a wide net |

**Threshold is a business policy, not a model parameter.**

## Three Population Segments

The clustering algorithm identified 3 distinct life-stage groups. These are the final business-facing segments.

**Segment 0: Senior/Retired Householders** (20%) — Retirement products, estate planning. 2.2% >$50K.

**Segment 1: Youth & Dependents** (33%) — Family-indirect marketing, youth savings. 0.05% >$50K.

**Segment 2: Mid-Career Working Householders** (47%) — Premium products, wealth management. 12.5% >$50K, 2x population average.

## Using Both Layers Together

1. **Score everyone** with the classifier
2. **Filter or rank** using a threshold appropriate to budget
3. **Customize messaging** by segment: investment for Segment 2, retirement for Segment 0

## Risks and Limitations

- Income is a proxy; validate against actual business outcomes in production
- Data is from 1994-1995; demographics have changed
- Segmentation is a useful lens, not ground truth
- Survey weights matter for population-level interpretation

## References

1. Dorogush et al. (2018). CatBoost: gradient boosting with categorical features support.
2. Pedregosa et al. (2011). Scikit-learn: Machine Learning in Python.
3. de Vos (2015). kmodes: k-modes and k-prototypes clustering.
4. Huang (1998). Extensions to the k-means algorithm for clustering large data sets with categorical values.
5. U.S. Census Bureau / BLS. Current Population Survey, 1994-1995.
6. Lundberg & Lee (2017). A Unified Approach to Interpreting Model Predictions.
