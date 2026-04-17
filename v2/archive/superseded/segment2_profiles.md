# Working-Age Sub-Segment Profiles

> Status: **Exploratory empirical result** — NOT an accepted Layer 2 operating segmentation
>
> **Lineage caveat**: This was run on a rules-based approximation of V1 Segment 2, not on the exact V1 K-Prototypes macro labels. See `second_pass_lineage_note.md` for details.

## Method Summary

- **Population**: Rules-based working-age approximation (116,329 rows, 58.3% of total)
- **Identification**: Age >= 18, education != "Children", NOT (age >= 55 AND weeks_worked < 10)
- **Note**: This is ~27% larger than V1 Segment 2 (91,443 rows) due to rules-based vs K-Prototypes differences
- **Method**: K-Prototypes, Cao init, gamma=0.5, n_init=5
- **Features**: 5 continuous + 9 categorical = 14 features
- **Subsample**: 20,000 random rows for fit
- **k evaluation**: k=3 through k=6 all produced micro-clusters (min < 1%)
- **Final**: k=3 → micro-cluster absorbed → **2 final sub-segments**

## Why Only 2 Sub-Segments

The working-age population, despite being large (116K rows), is dominated by a single structural split: **employed vs non-employed within working age**. The "Children or Armed Forces" CPS employment code captures a large group of working-age adults not in the detailed labor force (homemakers, discouraged workers, transitional). Every k >= 3 isolates a tiny outlier rather than finding meaningful additional structure.

This is a legitimate finding, not a failure. The data tells us that within working age, the primary differentiator is labor-force attachment — finer occupation/industry splits are not strong enough to dominate K-Prototypes clustering.

## Sub-Segment Summary

| Sub-Seg | Name | N | % of Working-Age | Wtd % | >50K Rate | Enrichment vs WA |
|---------|------|----:|--:|--:|--------:|--------:|
| 0 | **Active Workforce Earners** | 87,829 | 75.5% | ~76% | 13.24% | 1.30x |
| 1 | **Working-Age Non-Employed** | 28,500 | 24.5% | ~24% | 0.67% | 0.07x |

## Detailed Profiles

### Sub-Segment 0: Active Workforce Earners

**Who**: Mean age 40, primarily employed, majority married householders
- **Education**: HS grad 34%, some college 21%, bachelor's 17%
- **Marital**: Married 63%, never married 21%, divorced 10%
- **Sex**: Male 55%, female 45%
- **Occupation**: Admin support 15%, professional specialty 15%, exec/managerial 14%
- **Class of worker**: Private 70%, self-employed 8%, local govt 8%
- **Weeks worked**: Mean 49, median 52 (near full-year employment)
- **Tax filer**: Joint under 65: 62%, single: 28%
- **>50K rate**: 13.24% (1.3x working-age average)

**Marketing fit**: This is the primary commercial segment. Premium financial products, investment accounts, career-stage offers. High enough income enrichment to justify targeted campaigns.

### Sub-Segment 1: Working-Age Non-Employed

**Who**: Mean age 33, predominantly female, not in labor force
- **Education**: HS grad 33%, some college 23%, bachelor's 10%
- **Marital**: Married 47%, never married 38%
- **Sex**: Female 69%, male 31%
- **Occupation**: Not in universe 64% (not in detailed labor force), other service 8%
- **Class of worker**: Not in universe 63%, private 29%
- **Weeks worked**: Mean ~15, median likely 0 (low attachment)
- **Tax filer**: Nonfiler 38%, joint under 65: 35%
- **>50K rate**: 0.67% (0.07x working-age average — near-zero)

**Marketing fit**: Low direct income-targeting value. May be homemakers, students, or transitional. Better reached via household-level products (joint accounts, family insurance) or career-transition offers.

## Integration with V1 Macro Segments

The full V2 two-layer segmentation is now:

```
Population (199,523)
  |
  +-- Seniors (27,202, ~14%)           → retirement products
  +-- Youth/Dependents (55,992, ~28%)  → family-indirect
  +-- Working-Age (116,329, ~58%)
        |
        +-- Active Workforce (87,829)   → primary targeting segment
        +-- Non-Employed (28,500)       → household-indirect / transitional
```

*Note: The working-age identification uses rules-based criteria that capture a slightly different population than V1's K-Prototypes Segment 2. The conceptual structure is the same.*

## Limitations

1. Only 2 sub-segments emerged — finer splits were unstable
2. The employed/non-employed split is intuitive but may not add granularity beyond what the classifier already provides (employed people score higher)
3. The "Active Workforce" sub-segment (76% of working-age) is still large and internally diverse — further sub-segmentation within it would require different features or methods
4. Rules-based working-age identification is an approximation of V1 Seg 2
