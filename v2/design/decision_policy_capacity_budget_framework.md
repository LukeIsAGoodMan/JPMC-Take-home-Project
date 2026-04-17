# Decision Policy — Capacity & Budget Framework

> Status: **Complete** — empirical tables from V1-equivalent model; economics examples use assumed values

## Framework Overview

V1 chose thresholds by metric optimization (best F1 at precision >= X or recall >= Y). V2 reframes threshold selection as a **resource allocation problem**:

Given a budget (money) or capacity (time/staff), how should the business set its targeting threshold?

## Budget-Constrained Selection

**Logic**: The business has a fixed number of contacts it can afford. The model ranks everyone by score. Contact the top N.

### Budget-to-Threshold Mapping (empirical, validation set, 29,929 rows, 1,857 positives)

> Source: `v2_compute_results.json` — cumulative capture from V1-equivalent model.

| Top K Contacts | Score at Kth | True Positives | Precision | Recall |
|---------------:|-------------:|---------------:|----------:|-------:|
| 100 | 0.977 | 100 | 100.0% | 5.4% |
| 500 | 0.800 | 463 | 92.6% | 24.9% |
| 1,000 | 0.558 | 798 | 79.8% | 43.0% |
| 1,500 | 0.392 | 1,036 | 69.1% | 55.8% |
| 2,000 | 0.277 | 1,214 | 60.7% | 65.4% |
| 3,000 | 0.156 | 1,440 | 48.0% | 77.5% |
| 5,000 | 0.065 | 1,639 | 32.8% | 88.3% |

### Diminishing Returns (empirical)

| Increment | Marginal TP | TP per Marginal Contact |
|-----------|------------|----------------------:|
| 0 → 500 | 463 | 0.93 |
| 500 → 1,000 | 335 | 0.67 |
| 1,000 → 1,500 | 238 | 0.48 |
| 1,500 → 2,000 | 178 | 0.36 |
| 2,000 → 3,000 | 226 | 0.23 |
| 3,000 → 5,000 | 199 | 0.10 |

**The budget knee is around 1,500-2,000 contacts** — marginal yield per contact drops below 0.36 beyond that point.

## Capacity-Constrained Selection

**Logic**: The business has a fixed number of advisor appointments or phone slots. Each contact requires real human capacity.

| Capacity | Recommended Mode | Reasoning |
|----------|-----------------|-----------|
| < 500 appointments | Band A only (t >= 0.50) | Maximize hit rate per appointment |
| 500-1,500 appointments | Bands A+B (t >= 0.30) | Good balance of volume and quality |
| 1,500-3,000 appointments | Bands A+B+C (t >= 0.15) | Fill capacity, accept lower marginal precision |
| > 3,000 or digital-only | All viable bands (t >= 0.05) | Digital cost is low; cast wide net |

## Simple Value/Cost Threshold Rule

If the business can estimate:
- **V** = expected value of correctly identifying a >$50K individual
- **C** = cost per contact attempt

Then the break-even threshold is:

> **Contact if P(>50K | score) > C / V**

### Worked Examples

| Scenario | V | C | Break-even P | Approx Threshold |
|----------|---|---|-------------|------------------|
| Premium product advisor call | $500 | $100 | 0.20 | ~0.20 |
| Direct mail campaign | $200 | $5 | 0.025 | ~0.05 |
| Digital display ad | $50 | $1 | 0.02 | ~0.05 |
| VIP onboarding program | $2,000 | $500 | 0.25 | ~0.25 |

**Important caveat**: These V and C values are assumed, not observed. In production, they would be calibrated against real campaign data. The framework itself is sound; the inputs need validation.

## What This Framework Requires (and Doesn't Have)

| Input | Available? | Impact |
|-------|-----------|--------|
| Score distribution | Yes (from V1 model) | Enables budget-to-threshold mapping |
| Precision/recall by threshold | Yes (from V1 sweep) | Enables hit-rate estimation |
| Cost per contact (C) | **No — assumed** | Critical for V/C threshold rule |
| Value per true positive (V) | **No — assumed** | Critical for V/C threshold rule |
| Response rate | **No — census data has none** | Would upgrade from Tier 0 to Tier 2 targeting |
| Revenue attribution | **No** | Would enable Tier 3 expected-value optimization |

The framework is **structurally complete but empirically incomplete** — it shows the right decision logic even though the economic inputs are illustrative.
