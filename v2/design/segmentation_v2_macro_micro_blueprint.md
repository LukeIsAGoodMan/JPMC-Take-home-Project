# Segmentation V2 — Macro + Micro Blueprint

## 1. V1 Macro Segmentation (Frozen)

V1 produced 3 life-stage macro segments:

| Seg | Name | Wtd Share | >50K Rate | Enrichment |
|-----|------|----------|-----------|------------|
| 0 | Senior/Retired Householders | 20.1% | 2.2% | 0.35x |
| 1 | Youth/Dependent Non-Workforce | 33.1% | 0.05% | 0.01x |
| 2 | Mid-Career Working Householders | 46.7% | 12.5% | 2.12x |

These macro segments are **preserved as Layer 1** in V2. They capture the dominant life-stage structure and are useful for high-level campaign design.

## 2. Why Macro Is Not Enough

The V1 macro segmentation has a commercial limitation: **Segment 2 contains 47% of the population.** It's the primary targeting opportunity, but it treats all working-age adults the same — a 25-year-old entry-level retail worker and a 50-year-old self-employed professional with capital gains are both "Mid-Career Working Householders."

V2 addresses this by adding a **Layer 2 micro-segmentation within Segment 2**.

## 3. V2 Two-Layer Segmentation Architecture

```
Full Population (199,523)
    |
    +-- Layer 1: Macro Segments (V1, frozen)
    |       |
    |       +-- Seg 0: Seniors (20%)     → retirement marketing
    |       +-- Seg 1: Youth (33%)       → family-indirect
    |       +-- Seg 2: Working-Age (47%) → *** Layer 2 ***
    |
    +-- Layer 2: Micro Segments (V2, within Seg 2 only)
            |
            +-- Sub-segment A: [to be determined by clustering]
            +-- Sub-segment B: [to be determined by clustering]
            +-- Sub-segment C: [to be determined by clustering]
            +-- (possibly D)
```

## 4. Working-Age Segment Profile (V1 Data)

The V2 second-pass operates on Segment 2 (91,443 rows, 46.7% weighted):

| Feature | Distribution |
|---------|-------------|
| Age | Mean 39, median 38 |
| Education | HS grad 33%, some college 21%, bachelor's 17% |
| Marital | Married 62%, never married 22%, divorced 10% |
| Sex | Male 54%, female 46% |
| Top occupations | Admin support 15%, professional specialty 14%, exec/managerial 13% |
| Employment | Full-time 41%, "Children or Armed Forces" 50% (CPS code for non-detailed) |
| Class of worker | Private 70%, self-employed 8%, local govt 8% |
| Weeks worked | Mean 49, median 52 |
| Tax filer | Joint under 65: 60%, single: 30% |
| >$50K rate | 12.5% (2.1x population enrichment) |

This is a **diverse group** with clear internal variation along economic, occupational, and household dimensions.

## 5. Hypothesized Sub-Segments

Based on the feature distributions, plausible sub-segments within the working-age group include:

| Hypothesis | Key Distinguishing Features | Expected Prevalence | Marketing Fit |
|-----------|---------------------------|--------------------:|---------------|
| **Emerging professionals** | Age 25-35, bachelor's+, professional/exec occupation, single | ~15-20% of seg 2 | Career products, student loan refi, starter investment |
| **Established family earners** | Age 35-50, married, joint filer, full-time, moderate-high weeks | ~25-30% of seg 2 | Family financial planning, mortgage, insurance |
| **Self-employed / business-oriented** | Self-employed flag, higher capital gains/dividends | ~8-10% of seg 2 | Business banking, tax planning, commercial products |
| **Service / hourly workers** | HS education, retail/service industry, lower weeks worked | ~20-25% of seg 2 | Basic banking, payroll products, accessible credit |
| **Asset-income / premium-fit** | High capital gains + dividends, exec/professional occupation | ~5-10% of seg 2 | Wealth management, investment advisory |

**These are hypotheses, not final segments.** They guide the clustering feature selection and k evaluation in Phase 2.

## 6. Second-Pass Clustering Design

### 6a. Input Data

- **Population**: Segment 2 rows only (91,443 records)
- **Method**: K-Prototypes (same as V1 — mixed data)
- **Fit strategy**: Random subsample (~15,000-20,000 rows), predict full segment

### 6b. Feature Selection for Second Pass

The second-pass should use features that **differentiate within** the working-age group, not features that distinguish life-stages (which Layer 1 already handles).

| Feature | Include? | Rationale |
|---------|----------|-----------|
| education | Yes | Differentiates human-capital tiers |
| major occupation code | Yes | Occupational type is key economic differentiator |
| major industry code | Yes | Industry context for occupation |
| class of worker | Yes | Private vs self-employed vs govt |
| tax filer stat | Yes | Household economic structure |
| marital stat | Yes | Family stage within working-age |
| own business or self employed | Yes | Self-employment indicator |
| weeks worked in year | Yes | Work attachment intensity |
| capital gains | Yes | Investment/wealth signal |
| dividends from stocks | Yes | Asset-income signal |
| wage per hour | Yes | Earning rate |
| age | Yes | Career-stage differentiator within 20-65 range |
| sex | Maybe | Relevant for some product segments |
| detailed household summary | Maybe | Could be redundant with marital + tax filer |
| family members under 18 | No | ~99% "Not in universe" in this segment — no variation |
| citizenship | Maybe | Low variance in this segment (87% native-born) |

**Estimated: 12-14 features** for the second-pass clustering.

### 6c. k Range

Evaluate k = 3 through 6 for the second pass. The working-age population is more homogeneous than the full population, so fewer macro-groups are expected.

### 6d. Governance

Same as V1:
- Target excluded from clustering input (profiled ex post)
- Weight excluded from clustering input (used for sizing only)
- Absorption rule for micro-clusters (< 3% of segment 2)

## 7. Two Segmentation Tracks

### Operational Track
- Curated feature subset (12-14 features per section 6b)
- K-Prototypes with Cao init
- Optimized for interpretability and actionability
- This is the primary second-pass output

### Exploratory Track
- Broader feature pool (all 31 classification features available in seg_full.csv)
- Discovery-oriented: does broader input reveal structure that the curated set misses?
- Results compared to operational track but NOT automatically adopted
- Used to test whether human curation is suppressing meaningful structure

## 8. Feature Inclusion Rubric (V2)

V1's feature selection was curated but informal. V2 formalizes the criteria:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Business relevance | High | Does this feature help a marketer differentiate customers? |
| Cardinality burden | Medium | High-cardinality features (50+ levels) add noise to K-Prototypes |
| Sentinel burden | Medium | Features with >80% "Not in universe" have limited variation |
| Redundancy | Medium | Does this feature duplicate information already in the set? |
| Stability contribution | Low-Medium | Does this feature help produce stable, reproducible clusters? |
| Actionability | High | Can the business act differently based on this feature? |

This rubric will be applied formally in `segmentation_feature_scorecard.md` during Phase 2.

## 9. Actual V2 Segmentation Output (Exploratory)

The second-pass clustering was executed on a rules-based working-age approximation (116,329 rows). It produced **2 sub-segments** after micro-cluster absorption:

```
Layer 1 (Macro, from V1 — frozen):
  Seg 0: Seniors (20%)
  Seg 1: Youth (33%)
  Seg 2: Working-Age (47%)

Layer 2 (Exploratory, within rules-based working-age approximation):
  Sub-0: Active Workforce Earners (76% of WA, 13.2% >50K)
  Sub-1: Working-Age Non-Employed (24% of WA, 0.67% >50K)
```

**This is an exploratory result, not a formally adopted Layer 2.** It used a rules-based approximation of V1 Segment 2 (see `second_pass_lineage_note.md`), and the 2-sub-segment outcome is coarser than originally hypothesized.

The finding is directionally informative: within working-age, the primary structural differentiator is labor-force attachment. Finer occupation/industry-level splits were unstable in K-Prototypes.

## 10. Implementation Status

| Component | Status | Type |
|-----------|--------|------|
| Macro layer (V1) | **Frozen** | Adopted baseline |
| Second-pass design | **Complete** | Design artifact |
| Feature scorecard rubric | **Complete** | Design artifact |
| Second-pass clustering | **Executed** | Exploratory empirical (rules-based population) |
| Sub-segment profiling | **Complete** | Exploratory empirical |
| Formal Layer 2 adoption | **Not done** | Requires exact V1 labels + re-evaluation |
| Score x sub-segment integration | **Provisional** | Uses exploratory sub-segments |
