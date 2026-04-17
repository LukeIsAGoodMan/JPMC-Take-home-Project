# Score-Band Analysis

> Status: **Empirical result** — computed from V1-equivalent model on validation set

## Score Distribution

The V1 CatBoost model produces continuous probabilities (0-1) on the 29,929-row validation set.

| Statistic | Value |
|-----------|------:|
| Mean score | 0.061 |
| Median score | 0.004 |
| 90th percentile | 0.156 |
| 95th percentile | 0.393 |
| 99th percentile | 0.903 |
| Actual positive rate | 6.21% |

The distribution is **heavily right-skewed**: 81% of the population scores below 0.05, and only 6.3% scores above 0.15. This matches the rare-event nature of the target.

## Score-Band Breakdown

| Band | Score Range | N | % of Pop | Positives | Precision | Interpretation |
|------|-----------|----:|--------:|---------:|----------:|---------------|
| **A: Very High** | >= 0.50 | 1,133 | 3.8% | 876 | 77.3% | Strong confidence — premium outreach |
| **B: High** | 0.30 – 0.50 | 739 | 2.5% | 298 | 40.3% | Likely positive, some uncertainty |
| **C: Marginal** | 0.15 – 0.30 | 1,209 | 4.0% | 277 | 22.9% | Business decision zone |
| **D: Low** | 0.05 – 0.15 | 2,672 | 8.9% | 230 | 8.6% | Below base-rate enrichment threshold |
| **E: Very Low** | < 0.05 | 24,176 | 80.8% | 176 | 0.7% | Near-zero probability |

### Key Observations

1. **Band A captures 47% of all positives** in just 3.8% of the population — this is the core high-value targeting zone.
2. **Bands A+B together capture 63% of positives** in 6.3% of the population — efficient targeting with good hit rate.
3. **Band C is the marginal decision zone**: 4% of population, 22.9% precision. Whether to include Band C depends on budget and cost-per-contact.
4. **Band E is 81% of the population** — these are confidently-predicted non-targets. Excluding them saves budget without meaningful loss.

## Cumulative Capture Analysis

Ranking everyone by score (descending) and selecting the top-k:

| Top K | True Positives | Recall | Precision | Score at Kth Position |
|------:|---------------:|-------:|----------:|----------------------:|
| 100 | 100 | 5.4% | 100.0% | 0.977 |
| 500 | 463 | 24.9% | 92.6% | 0.800 |
| 1,000 | 798 | 43.0% | 79.8% | 0.558 |
| 1,500 | 1,036 | 55.8% | 69.1% | 0.392 |
| 2,000 | 1,214 | 65.4% | 60.7% | 0.277 |
| 3,000 | 1,440 | 77.5% | 48.0% | 0.156 |
| 5,000 | 1,639 | 88.3% | 32.8% | 0.065 |

> Source of truth: `v2_compute_results.json` — all values from canonical JSON.

### Diminishing Returns

| Increment | Marginal TP | Marginal TP per Contact |
|-----------|------------|----------------------:|
| 0 → 500 | 463 | 0.93 |
| 500 → 1,000 | 335 | 0.67 |
| 1,000 → 1,500 | 238 | 0.48 |
| 1,500 → 2,000 | 178 | 0.36 |
| 2,000 → 3,000 | 226 | 0.23 |
| 3,000 → 5,000 | 199 | 0.10 |

**The "budget knee" is around 1,500-2,000 contacts** on this validation set — marginal yield drops sharply beyond that point.

## Implications for Decision Policy

1. **Budget < 1,000**: Band A only. Very high precision, miss half the positives but budget demands it.
2. **Budget 1,000-2,000**: Bands A+B. Good precision-recall balance. This is the sweet spot.
3. **Budget 2,000-3,500**: Include Band C. Marginal cases — segment-conditional thresholds add the most value here.
4. **Budget > 3,500**: Include Band D. Low marginal yield; only justified for very low-cost digital campaigns.
