# Second-Pass Segmentation — Execution Design

> Status: **Executed (exploratory)** — clustering was run on a rules-based population approximation; result is exploratory, not formally adopted

## Objective

Sub-segment the V1 working-age macro segment (~47% of population) into more commercially useful groups. The macro segment treats all working-age adults identically; the second pass should differentiate by economic tier, occupation type, and household situation.

## Population

Working-age segment identified by: age >= 18, education != "Children", AND NOT (age >= 55 AND weeks_worked < 10). This is a rules-based approximation of the V1 K-Prototypes Segment 2. Expected: ~90,000-95,000 rows.

## Clustering Method

K-Prototypes (same as V1) — appropriate for mixed numeric/categorical data.

## Input Features (14 total)

### Required (9 features)
| Feature | Type | Rationale |
|---------|------|-----------|
| age | continuous | Career-stage differentiator |
| weeks worked in year | continuous | Work attachment intensity |
| capital gains | continuous | Investment/wealth signal |
| dividends from stocks | continuous | Asset-income signal |
| wage per hour | continuous | Earning rate |
| education | categorical | Human-capital tier |
| major occupation code | categorical | Occupational type |
| class of worker | categorical | Private vs self-employed vs govt |
| tax filer stat | categorical | Household economic structure |

### Included (5 features)
| Feature | Type | Rationale |
|---------|------|-----------|
| marital stat | categorical | Family stage |
| sex | categorical | Product-relevant demographic |
| major industry code | categorical | Industry context |
| own business or self employed | categorical | Self-employment flag |
| detailed household summary | categorical | Household role |

### Excluded
| Feature | Why |
|---------|-----|
| family members under 18 | 99% "Not in universe" in this segment — no variation |
| citizenship | 87% native-born — low variation |
| All V1 review columns | Already excluded in V1 |
| target, weight | Governance: excluded from clustering input |

## Parameters

- **gamma**: 0.5 (same as V1 — balance numeric vs categorical)
- **Init**: Cao
- **n_init**: 3 for k evaluation, 5 for final fit
- **Subsample**: 20,000 random rows for fit, predict full segment
- **k range**: 3 to 6
- **Micro-cluster rule**: absorb clusters < 3% of working-age segment

## Expected Output

3-5 sub-segments within the working-age population, each with:
- Weighted size and share (of working-age segment)
- >50K enrichment (profiling only)
- Top defining features
- Business-readable name
- Marketing recommendation
