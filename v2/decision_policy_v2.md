# Decision Policy V2

## 1. V1 Baseline

V1 defined three fixed operating thresholds:

| Mode | Threshold | Precision | Recall | Predicted Positives (val) |
|------|-----------|-----------|--------|--------------------------|
| Precision-leaning | 0.45 | 0.726 | 0.510 | 1,304 |
| Balanced | 0.25 | 0.585 | 0.683 | 2,169 |
| Recall-leaning | 0.20 | 0.532 | 0.732 | 2,556 |

This was a significant improvement over the default 0.5 threshold. V2 goes further.

## 2. What V1 Missed

V1's threshold modes are **metric-driven** (maximize F1 under a precision or recall constraint). They don't directly incorporate:

- **Budget**: how many contacts can the campaign afford?
- **Capacity**: how many advisor appointments are available?
- **Economics**: what's the value of a true positive vs the cost of a false positive?
- **Score distribution**: where do most people fall, and what happens in marginal zones?

## 3. Score-Band Framework

V2 replaces fixed thresholds with a **score-band framework** that treats the model's continuous output as a prioritization ranking.

### Proposed Score Bands

| Band | Score Range | Interpretation | Typical Action |
|------|-----------|----------------|----------------|
| **A — Very High** | >= 0.50 | Strong confidence >$50K | Premium outreach, advisor contact |
| **B — High** | 0.30 – 0.50 | Likely >$50K, some uncertainty | Targeted digital, mid-touch |
| **C — Marginal** | 0.15 – 0.30 | Borderline — business decision matters most here | Campaign-dependent |
| **D — Low** | 0.05 – 0.15 | Unlikely >$50K but not excluded | Broad digital only if budget allows |
| **E — Very Low** | < 0.05 | Almost certainly <= $50K | Exclude from income-targeted campaigns |

### What V1 Data Shows by Band (validation set)

From the V1 threshold sweep:

| Score Range | Approx Volume | Cumulative Recall | Marginal Precision |
|------------|--------------|-------------------|-------------------|
| >= 0.50 | ~1,133 | 47.2% | 77.3% |
| 0.30 – 0.50 | ~739 | 63.2% | ~44% |
| 0.20 – 0.30 | ~684 | 73.2% | ~33% |
| 0.10 – 0.20 | ~1,365 | 83.7% | ~22% |
| 0.05 – 0.10 | ~1,832 | 90.5% | ~11% |
| < 0.05 | ~24,176 | 100% | ~1% |

**Key insight**: Band C (0.15–0.30) is the **marginal zone** where the business decision matters most. People in this band could go either way — the threshold policy determines whether they're contacted.

## 4. Budget-Constrained Threshold Selection

Instead of choosing a threshold by metric preference, V2 proposes choosing by **budget**:

### Framework

Given:
- Campaign budget allows **N contacts**
- Model ranks everyone by score (descending)
- Contact the top N

The business question becomes: "For a budget of N contacts, what precision and recall do I get?"

### Budget-to-Outcome Table (validation set, 29,929 rows)

| Budget (contacts) | Approx Threshold | Precision | Recall | Expected True Positives |
|-------------------|-----------------|-----------|--------|------------------------|
| 500 | ~0.60 | ~81% | ~22% | ~405 |
| 1,000 | ~0.50 | ~77% | ~42% | ~770 |
| 1,500 | ~0.40 | ~70% | ~56% | ~1,050 |
| 2,000 | ~0.30 | ~63% | ~63% | ~1,260 |
| 2,500 | ~0.20 | ~53% | ~73% | ~1,325 |
| 3,500 | ~0.10 | ~40% | ~84% | ~1,400 |
| 5,000 | ~0.05 | ~29% | ~91% | ~1,450 |

**Diminishing returns are visible**: doubling the budget from 1,000 to 2,000 contacts adds ~490 true positives. Doubling again from 2,000 to 4,000 adds only ~200 more.

## 5. Simple Value/Cost Framework

If the business can estimate:
- **V** = value of correctly identifying a >$50K individual (e.g., expected product revenue)
- **C** = cost of contacting someone (e.g., advisor time, mailing cost)

Then the optimal threshold satisfies:

> Contact if: P(>$50K | score) > C / V

**Example**:
- If V = $500 (expected revenue from premium product conversion) and C = $25 (cost per contact):
- Threshold: C/V = 0.05 → contact everyone above 5% probability
- If C = $100 (advisor appointment): threshold = 0.20
- If C = $200 (premium onboarding): threshold = 0.40

This is a simplified expected-value framework. In production, it would be enriched with response-rate data (Tier 2 targets from the target hierarchy).

## 6. Segment-Conditional Thresholds

V2 proposes that thresholds could vary by segment:

| Segment | Suggested Policy | Rationale |
|---------|-----------------|-----------|
| Senior/Retired (Seg 0) | Higher threshold (0.40+) | Low base rate (2.2%), need high confidence to justify outreach |
| Youth/Dependent (Seg 1) | Exclude from income targeting | Near-zero incidence (0.05%); family-indirect only |
| Working-Age (Seg 2) | Default or lower threshold (0.20–0.30) | Highest base rate (12.5%), most contacts will be in this segment anyway |

This connects the score layer and the segment layer into a unified decision.

## 7. V2 vs V1 Decision Framework

| Dimension | V1 | V2 |
|-----------|-----|-----|
| Threshold choice | 3 fixed modes (metric-driven) | Budget/capacity/value-driven |
| Score treatment | Binary at threshold | Continuous score bands |
| Segment interaction | Described but not formalized | Segment-conditional thresholds |
| Economic framing | Not included | Simple V/C framework |
| Marginal-case analysis | Not included | Band C (0.15–0.30) identified as decision zone |

## 8. Implementation Status

| Component | Status | Phase |
|-----------|--------|-------|
| Score-band definition | **Designed** (this doc) | Phase 1 |
| Budget-to-outcome table | **Estimated** from V1 sweep | Phase 1 |
| V/C framework | **Designed** (this doc) | Phase 1 |
| Segment-conditional thresholds | **Proposed** | Phase 2 |
| Actual score-band computation on full data | Not yet | Phase 2 |
| Score x Segment operating matrix | Not yet | Phase 2 (Workstream D) |
