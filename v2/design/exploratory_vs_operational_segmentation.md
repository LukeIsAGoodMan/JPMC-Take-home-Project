# Exploratory vs Operational Segmentation

> Status: **Completed design artifact**

## Two-Track Design

V2 defines two segmentation tracks. They serve different purposes and should not be confused.

### Operational Track (primary)

**Goal**: Produce business-facing sub-segments within the working-age population that a marketing team can act on.

| Attribute | Choice |
|-----------|--------|
| Feature set | Curated 14 features (scorecard-evaluated) |
| Method | K-Prototypes, Cao init, gamma=0.5 |
| k selection | Viability-constrained (min cluster >= 3-5%) |
| Naming | Required — every segment gets a business-readable name |
| Profiles | Detailed — demographics, employment, income enrichment |
| Actionability | Required — marketing recommendation per segment |
| Adoption | Intended for business-facing delivery |

### Exploratory Track (secondary)

**Goal**: Test whether the curated feature selection is suppressing meaningful structure.

| Attribute | Choice |
|-----------|--------|
| Feature set | All 31 V1 classification features available in seg_full.csv |
| Method | Same K-Prototypes (for comparability) |
| k selection | Less constrained — allow smaller clusters for discovery |
| Naming | Optional — exploration may produce unnamed clusters |
| Profiles | Summary-level — enough to compare with operational track |
| Actionability | Not required |
| Adoption | NOT automatically adopted; used for diagnostic comparison |

## How to Compare Them

| Question | If Yes | If No |
|----------|--------|-------|
| Does the exploratory track find a sub-group the operational track missed? | Investigate whether adding the relevant features to the operational set improves it | Confirms the curated set is sufficient |
| Does the exploratory track produce more stable clusters? | Consider broadening the feature set | Confirms curation helps |
| Does the exploratory track produce clusters that are harder to name? | Accept that the extra features add noise, not signal | N/A |

## Current Status

| Track | Status | Notes |
|-------|--------|-------|
| Operational | **Executed (exploratory)** | Ran on rules-based population approximation; produced 2 sub-segments; NOT formally adopted due to lineage gap |
| Broader exploratory | **Deferred** | Designed but not executed |

**Important**: The operational track was executed but its result is classified as **exploratory** because it used a rules-based approximation of V1 Segment 2 rather than exact V1 macro labels. See `second_pass_lineage_note.md`.

The 2-sub-segment result (Active Workforce vs Non-Employed) is informative and directionally useful, but is not promoted to formal Layer 2 status. For formal adoption, the second-pass would need to be re-run on the exact V1 K-Prototypes Segment 2 population.
