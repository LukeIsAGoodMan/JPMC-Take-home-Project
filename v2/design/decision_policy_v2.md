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

### Empirical Score-Band Breakdown (validation set, 29,929 rows, 1,857 positives)

> Source: `v2_compute_results.json` — V1-equivalent model retrained with frozen hyperparameters.

| Band | Score Range | N | % of Pop | Positives | Precision |
|------|-----------|----:|--------:|---------:|----------:|
| A: Very High | >= 0.50 | 1,133 | 3.8% | 876 | 77.3% |
| B: High | 0.30 – 0.50 | 739 | 2.5% | 298 | 40.3% |
| C: Marginal | 0.15 – 0.30 | 1,209 | 4.0% | 277 | 22.9% |
| D: Low | 0.05 – 0.15 | 2,672 | 8.9% | 230 | 8.6% |
| E: Very Low | < 0.05 | 24,176 | 80.8% | 176 | 0.7% |

**Key insight**: Band C (0.15–0.30) is the **marginal zone** where the business decision matters most. Bands A+B capture 63% of all positives in just 6.3% of the population.

## 4. Budget-Constrained Threshold Selection

Instead of choosing a threshold by metric preference, V2 proposes choosing by **budget**:

### Framework

Given:
- Campaign budget allows **N contacts**
- Model ranks everyone by score (descending)
- Contact the top N

The business question becomes: "For a budget of N contacts, what precision and recall do I get?"

### Budget-to-Outcome Table (empirical, validation set, 29,929 rows, 1,857 positives)

| Top K Contacts | Score at Kth | True Positives | Precision | Recall |
|---------------:|-------------:|---------------:|----------:|-------:|
| 100 | 0.977 | 100 | 100.0% | 5.4% |
| 500 | 0.800 | 463 | 92.6% | 24.9% |
| 1,000 | 0.558 | 798 | 79.8% | 43.0% |
| 1,500 | 0.392 | 1,036 | 69.1% | 55.8% |
| 2,000 | 0.277 | 1,214 | 60.7% | 65.4% |
| 3,000 | 0.156 | 1,440 | 48.0% | 77.5% |
| 5,000 | 0.065 | 1,639 | 32.8% | 88.3% |

> Source of truth: `v2_compute_results.json`

**Diminishing returns are empirically clear**: the first 500 contacts yield 463 TP (0.93 per contact). Contacts 2,000-3,000 yield only 226 TP (0.23 per contact).

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

| Component | Status | Type |
|-----------|--------|------|
| Score-band definition + empirical breakdown | **Complete** | Empirical result |
| Budget-to-outcome table (top-k) | **Complete** | Empirical result |
| V/C framework | **Complete** | Design with assumed economics |
| Segment-conditional thresholds | **Proposed** | Design artifact |
| Score x Segment operating matrix | **Complete** (macro); exploratory (micro) | Design + exploratory |
