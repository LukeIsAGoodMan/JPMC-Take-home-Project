# Score x Segment Operating Matrix

> Status: **Design artifact** — macro matrix is grounded; micro matrix uses exploratory sub-segments (not formally adopted)

## Concept

The V1 project produces two independent outputs per individual:
1. **Income score** (0-1 continuous probability from CatBoost)
2. **Macro segment** (one of 3 life-stage groups from K-Prototypes)

V2 adds a third dimension:
3. **Micro sub-segment** (within working-age, from second-pass clustering)

The operating matrix defines **what action to take** for each combination.

## Macro Operating Matrix (V1 Segments x Score Bands)

| | Band A (>=0.50) | Band B (0.30-0.50) | Band C (0.15-0.30) | Band D (<0.15) |
|-|----------------|--------------------|--------------------|----------------|
| **Seg 0: Seniors** | Retirement wealth mgmt (rare — low base rate) | Retirement planning | Standard retirement products | Exclude from income targeting |
| **Seg 1: Youth** | *Almost empty* | *Almost empty* | *Almost empty* | Family-indirect only |
| **Seg 2: Working-Age** | Premium outreach | Targeted digital | Campaign-dependent | Broad digital or exclude |

### Key observations

- **Seg 1 x any score band**: Nearly empty of high-income individuals (0.05% base rate). The score is irrelevant here — this segment is always family-indirect.
- **Seg 0 x Band A**: Very small population (seniors rarely score very high) but high-confidence when they do — retirement wealth management opportunities.
- **Seg 2 x Bands A+B**: The primary commercial zone. Most of the model's value concentrates here.
- **Seg 2 x Band C (marginal zone)**: This is where threshold policy and sub-segmentation matter most. An Active Workforce member in Band C is a different decision than a Non-Employed working-age person in Band C.

## Micro Operating Matrix (Exploratory Working-Age Sub-Segments x Score Bands)

> **Exploratory**: These sub-segments are from the rules-based second-pass (not exact V1 labels). Treat as provisional guidance.

| | Band A (>=0.50) | Band B (0.30-0.50) | Band C (0.15-0.30) | Band D (<0.15) |
|-|----------------|--------------------|--------------------|----------------|
| **Active Workforce** (76% of WA) | Premium outreach — investment, wealth mgmt | Targeted digital, career-stage offers | Campaign-dependent: profession/industry should guide | Core banking, broad digital |
| **Non-Employed WA** (24% of WA) | *Very rare* — household-level wealth offers | *Rare* — transitional/family offers | Household-indirect only | Exclude from individual income targeting |

## Decision Rules

### Rule 1: Score gates access; segment customizes approach
- Use the score threshold to decide *whether* to contact
- Use the segment to decide *how* to contact

### Rule 2: Marginal cases benefit most from segmentation
- For Band A (>=0.50): segment matters for messaging but the contact decision is clear
- For Band C (0.15-0.30): segment helps determine whether the marginal contact is worth the cost
  - An Active Workforce member in Band C may be worth a lighter-touch digital campaign
  - A Non-Employed working-age person in Band C is likely not worth individual income-based outreach

### Rule 3: Budget allocation follows the matrix
- Expensive campaigns: target Band A across segments (high precision)
- Mid-tier campaigns: target Bands A+B, customize by segment
- Broad campaigns: target Bands A+B+C, use segment for creative/channel only
