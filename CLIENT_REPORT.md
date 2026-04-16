# Client Report: Income Targeting & Customer Segmentation

## Executive Summary

We built two complementary tools for retail targeting using CPS census data (199,523 individuals, 1994-1995):

1. **An income scoring model** that identifies individuals likely to earn more than $50,000. The model achieves strong discriminative performance (ROC-AUC 0.96, PR-AUC 0.70 on held-out test data) and can be tuned to different operating modes depending on the business use case.

2. **A population segmentation** that divides the population into 3 actionable groups based on life-stage, employment, and household patterns — each suggesting different marketing approaches.

Together, these form a **two-layer targeting design**: the classifier tells you *who to prioritize*, and the segmentation tells you *how to approach them*.

## The Business Problem

A retail client wants to identify high-income individuals for premium product targeting. The census data provides demographic, employment, and household variables but no direct transaction or response data. Income above $50,000 serves as a proxy for purchasing power and product affinity.

**Important framing**: Income is a *proxy target*, not the ultimate business objective. What the client actually cares about is likely a combination of purchasing power, product fit, and propensity to respond. The classifier should be treated as a prioritization and routing tool — it ranks people by likelihood of being high-income, which the business can then combine with other signals.

## How to Use the Classifier

### The Model Produces a Score, Not a Decision

The classifier outputs a probability between 0 and 1 for each individual. This probability represents how likely the person is to earn above $50K based on their demographic and employment profile.

The business decision is *what to do with that score*, and that depends on the use case:

### Three Operating Modes

| Mode | When to Use | Threshold | What You Get |
|------|-------------|-----------|-------------|
| **Precision-leaning** | Expensive outreach (personal advisor calls, premium mailers) | 0.45 | 73% of flagged people are truly >$50K, but you miss half of them |
| **Balanced** | General targeting and reporting | 0.25 | Best overall balance — 58% precision, 68% recall |
| **Recall-leaning** | Broad screening (don't miss anyone eligible) | 0.20 | Catches 73% of high-income people, but more false positives |

### Practical Example

Imagine a campaign offering a premium credit card to high-income individuals:

- **Budget is tight?** Use precision-leaning (threshold 0.45). You'll contact fewer people but most of them will qualify. Lower volume, higher hit rate.
- **Coverage matters?** Use recall-leaning (threshold 0.20). You'll cast a wider net and find most high-income individuals, but more contacts will be below the income threshold.
- **Balanced campaign?** Use threshold 0.25. Best overall tradeoff for general-purpose targeting.

The key insight: **threshold is a business policy, not a model parameter.** The model's quality (its ranking ability) is the same regardless of threshold — what changes is the operating tradeoff.

## Why Threshold Policy Matters

Most classification projects report a single accuracy number. That approach fails here because the target class is rare (~6.2% of the population). A model that predicts "not high-income" for everyone would be 93.8% "accurate" but completely useless.

Instead, we focus on:
- **PR-AUC** (0.70): how well the model identifies the rare high-income class across all thresholds
- **ROC-AUC** (0.96): overall ranking quality
- **Threshold-specific precision/recall**: the operational tradeoff the business controls

This framing respects the reality that marginal cases (people near the decision boundary) are where the business value and risk concentrate. A hard 0/1 label hides this — a score with threshold policy makes it actionable.

## What the Segmentation Adds

The classifier tells you *who is likely high-income*. It does not tell you *who these people are* or *how to approach them*. That's what segmentation provides.

### Three Population Segments

The clustering algorithm identified 3 distinct life-stage groups across the full population. These are the final business-facing segments used throughout this report.

**Segment 0: Senior/Retired Householders** (20% of population)
- Mean age 63, mostly married, not in workforce
- Very low income incidence (2.2% >$50K)
- **Marketing angle**: Retirement income products, estate planning, Medicare supplements. Reach via direct mail, phone, community events.

**Segment 1: Youth & Dependents** (33% of population)
- Mean age 11, children and young dependents
- Almost no income (0.05% >$50K)
- **Marketing angle**: Family-indirect marketing through parents/guardians. Youth savings accounts, education products. Long-horizon relationship building.

**Segment 2: Mid-Career Working Householders** (47% of population)
- Mean age 39, primarily full-time employed, majority married householders
- Highest income concentration (12.5% >$50K, 2x population average)
- **Marketing angle**: Premium financial products, investment accounts, wealth management. Career-stage-appropriate offers. Digital and advisor channels.

### Using the Classifier and Segmentation Together

The most powerful approach combines both layers:

1. **Score everyone** with the classifier to get income likelihood
2. **Filter or rank** using a threshold appropriate to the campaign budget and objective
3. **Customize messaging** using segment membership:
   - A high-scoring person in Segment 2 gets premium investment messaging
   - A high-scoring person in Segment 0 gets retirement-focused messaging
   - Segment 1 is largely irrelevant for direct income targeting but matters for family-oriented products

This two-layer approach turns a statistical prediction into a marketing action plan.

## What the Model Relies On

The top predictive features are intuitive human-capital and household signals:

1. **Family members under 18** — household structure proxy
2. **Age** — career stage and earning trajectory
3. **Veterans benefits** — employment/benefits status indicator
4. **Weeks worked in year** — labor force attachment
5. **Sex** — demographic correlate of 1990s income distribution

The model does *not* rely on any single dominant feature, and the feature pattern is consistent with economic intuition: income is driven by career stage, work attachment, household structure, and education.

## Risks and Limitations

1. **Income is a proxy**. The >$50K label from 1994-1995 census data does not directly measure purchasing power, product affinity, or propensity to respond. In production, the targeting model should be validated against actual business outcomes (response rates, conversion, LTV).

2. **Historical data**. Demographics and income distributions have changed since 1994-1995. The model demonstrates methodology, not a production-ready deployment.

3. **Threshold choice has real consequences**. A precision-leaning threshold means missing many high-income individuals. A recall-leaning threshold means more contacts with lower hit rates. The business must decide which error is more costly.

4. **Segmentation is a lens, not ground truth**. The three segments reflect the dominant life-stage structure in the data. They are useful for organizing marketing thinking but are not the only valid segmentation — different feature subsets or methods would produce different groups.

5. **Survey weights matter for interpretation**. The CPS dataset uses survey weights to represent the US population. All population-level segment sizes and income rates are reported using these weights. Campaign-level metrics should be interpreted accordingly.

## What We Would Do Next

In a production engagement, the natural next steps would be:

1. **Validate against outcomes**: Connect the model to actual response/conversion data instead of the income proxy
2. **Refresh the data**: Retrain on current-year census or proprietary data
3. **Sub-segment the working-age group**: The largest segment (47%) contains both high-income and average-income individuals — the classifier's probability score provides a natural dimension for finer targeting within this group
4. **Build a response model**: If campaign response data becomes available, a propensity model would be more directly actionable than income prediction
5. **Operationalize threshold policy**: Build a simple decision tool that lets campaign managers select their operating mode and see the expected volume/precision tradeoff

## References

1. Dorogush, A.V., Ershov, V., & Gulin, A. (2018). CatBoost: gradient boosting with categorical features support. *arXiv:1810.11363*. [arxiv.org/abs/1810.11363](https://arxiv.org/abs/1810.11363)
2. Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. *JMLR*, 12, 2825-2830. Used for metrics, calibration, train-test splitting.
3. de Vos, N.J. (2015). kmodes: Python implementation of k-modes and k-prototypes clustering. [github.com/nicodv/kmodes](https://github.com/nicodv/kmodes)
4. Huang, Z. (1998). Extensions to the k-means algorithm for clustering large data sets with categorical values. *Data Mining and Knowledge Discovery*, 2(3), 283-304. Theoretical basis for K-Prototypes.
5. U.S. Census Bureau / Bureau of Labor Statistics. Current Population Survey (CPS), March Supplement, 1994-1995. Dataset source.
6. Lundberg, S.M. & Lee, S.-I. (2017). A Unified Approach to Interpreting Model Predictions. *NeurIPS*. SHAP framework used for feature interpretation.
