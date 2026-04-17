# Exact Second-Pass Segmentation — Design & Execution

> Status: **Executed on exact V1 Segment 2 population**

## Population

- **Source**: Exact V1 macro labels recovered via deterministic replay
- **Population**: V1 Segment 2 = 91,443 rows (45.8% of total)
- **Lineage**: Exact — verified against frozen V1 output sizes

## Method

- K-Prototypes, Cao init, gamma=0.5
- 14 features: 5 continuous + 9 categorical
- Random subsample: 20,000 rows (seed=43, offset from V1 seed)
- k evaluation: k=3 through k=6
- Final fit: k=4, n_init=5, max_iter=100
- Absorption: clusters < 3% of segment merged

## k Evaluation

| k | Cost | Smallest Cluster % |
|---|-----:|-------------------:|
| 3 | 107,376 | 0.4% |
| 4 | 93,056 | 0.4% |
| 5 | 79,970 | 0.4% |
| 6 | 75,781 | 0.4% |

All k values produce a persistent micro-cluster (~0.4%). Same structural pattern as V1 macro segmentation: one tiny outlier pocket at every k.

## Final Result

k=4 requested → micro-cluster absorbed → **3 sub-segments**:

| Sub-Seg | N | % of Seg 2 | >50K Rate | Enrichment vs Seg 2 |
|---------|----:|----------:|----------:|--------------------:|
| 0 | 34,904 | 38.2% | 20.66% | 1.65x |
| 1 | 10,239 | 11.2% | 2.39% | 0.19x |
| 2 | 46,300 | 50.6% | 8.61% | 0.69x |

## Multi-Seed Stability

| Seed | Final k | Segment Sizes |
|------|--------:|--------------|
| 42 (primary) | 3 | 34,904 / 10,239 / 46,300 |
| 52 | 3 | 73,196 / 11,010 / 7,237 |
| 62 | 3 | 47,069 / 34,120 / 10,254 |
| 72 | 2 | 79,447 / 11,996 |

**Stability assessment**: 3 of 4 seeds produce 3 sub-segments; 1 produces 2. The **existence of a ~10K low-income service-worker group** is consistent across all seeds. The split between the two larger groups is seed-dependent.
