# Campaign Playbook V2

> Status: **Completed design artifact**

## How to Use This Playbook

This playbook shows how three different campaign types use the classifier score, threshold policy, and segmentation together. It upgrades V1's simple 3-mode threshold into scenario-driven decision logic.

---

## Scenario 1: Premium Credit Card Launch (Budget-Constrained)

**Business context**: $200 cost per advisor appointment. Limited to 1,000 contacts. Need high hit rate.

**Threshold policy**: Band A only (score >= 0.50)
- Expected volume: ~1,100 from validation (~3.8% of population)
- Expected precision: ~77% — most contacts are truly high-income
- Expected recall: ~47% — misses half the high-income population but budget demands it

**Segment logic**:
| Segment | Action |
|---------|--------|
| Working-age Band A | Premium investment messaging, advisor appointment |
| Senior Band A | Retirement wealth management, estate planning angle |
| Youth Band A | Skip — near zero volume |

**V2 exploratory finding**: The second-pass segmentation split working-age into Active Workforce (76%) and Non-Employed (24%). Within Band A, nearly all contacts will be Active Workforce. The classifier score already prioritizes within this group; finer occupation-level sub-segments were not empirically stable in the current pass.

*Future opportunity*: If occupation-level sub-segmentation becomes available (see `segmentation_v2_macro_micro_blueprint.md`), differentiate creative by occupation type within Band A.

---

## Scenario 2: General Digital Targeting (Mid-Budget)

**Business context**: $10 cost per digital impression. Budget for 5,000-8,000 contacts. Balanced ROI.

**Threshold policy**: Bands A+B+C (score >= 0.15)
- Expected volume: ~3,100 from validation (~10% of population)
- Expected precision: ~47% at t=0.15
- Expected recall: ~78%

**Segment logic**:
| Segment | Action |
|---------|--------|
| Working-age Band A+B | Personalized digital ads — product-specific by sub-segment |
| Working-age Band C | Lighter-touch: brand awareness, content marketing |
| Senior Band B+ | Retirement-themed digital (email, display) |
| Youth | Excluded from income targeting; family-adjacent ads only |

**V2 exploratory finding**: Working-age contacts in Bands A+B are almost entirely Active Workforce sub-segment. Band C includes some Non-Employed working-age individuals who are lower-value targets — the sub-segment distinction helps deprioritize them.

*Future opportunity*: Occupation-level creative variants (professional vs service vs self-employed) would add value here but were not empirically achieved in this pass.

---

## Scenario 3: Broad Screening (High-Coverage)

**Business context**: Pre-approval screening for a mass-market product. Need to identify as many eligible individuals as possible. Low per-contact cost ($1-2 digital).

**Threshold policy**: Band A+B+C+D (score >= 0.05)
- Expected volume: ~5,800 from validation (~19% of population)
- Expected precision: ~29%
- Expected recall: ~91%

**Segment logic**:
| Segment | Action |
|---------|--------|
| All working-age | Include in screening pool |
| Seniors | Include — some have hidden wealth/income |
| Youth | Exclude unless product is family-oriented |

**V2 value-add**: At this threshold, the score mostly determines priority order for follow-up, not a hard include/exclude. Segment determines which product to pre-approve.

---

## Scenario 4: Market Sizing (No Outreach)

**Business context**: Estimate addressable market size for a new premium product line.

**Threshold policy**: Not applicable — use score distribution, not a binary cut.

**Approach**:
1. Use weighted segment sizes as population estimates
2. Within working-age segment, use sub-segment sizes for market decomposition
3. Apply >50K enrichment rates as premium-addressable share estimates

**Example output**:
- Working-age segment: 47% of population
- Of those, ~12.5% are >$50K (per V1 profiling)
- That's ~5.8% of the total population as the premium-addressable core
- Sub-segments within that core determine product-line sizing

---

## V1 vs V2 Playbook Comparison

| Aspect | V1 | V2 |
|--------|-----|-----|
| Threshold modes | 3 fixed (precision/balanced/recall) | Scenario-driven with budget/cost context |
| Segment usage | Mentioned but not formalized | Integrated into every scenario |
| Sub-segment logic | N/A | Micro-segment creative/product differentiation |
| Economic framing | None | Explicit cost-per-contact assumptions |
| Market sizing | Not included | Included as a non-outreach use case |
