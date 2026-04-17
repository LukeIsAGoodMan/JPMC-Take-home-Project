# Target Design V2

## 1. V1 Baseline Target

V1 uses a single binary target derived from the CPS income label:

| Raw Value | Mapped | Meaning |
|-----------|--------|---------|
| `- 50000.` | 0 | Income <= $50K |
| `50000+.` | 1 | Income > $50K |

**Prevalence**: 6.2% positive class (12,382 of 199,523).

V1 explicitly acknowledged this is a **proxy target** — income above a round threshold in 1994 dollars is not what a retail client ultimately optimizes for.

## 2. What's Wrong With the Current Target

| Limitation | Impact |
|-----------|--------|
| Binary at a round threshold | Loses all information about *how much* above or below $50K. A $51K earner and a $200K earner are treated identically. |
| 1994 dollars | $50K in 1994 ≈ $105K in 2024. The threshold doesn't map to current purchasing power. |
| Income ≠ purchasing power | Wealth, assets, household composition, and cost of living are missing. A $60K earner in rural Mississippi has more purchasing power than one in Manhattan. |
| Income ≠ product affinity | High income doesn't guarantee interest in premium financial products. Behavioral and attitudinal data would be stronger. |
| No response signal | We're predicting *who earns more*, not *who would respond to an offer*. These are different questions. |

## 3. Target Hierarchy

V2 introduces a structured target hierarchy — from what we have to what would be ideal:

### Tier 0: Current V1 Proxy (available now)
**Binary income > $50K**
- Already built and frozen
- PR-AUC 0.70, ROC-AUC 0.96
- Usable as a coarse first-pass screen

### Tier 1: Upgraded Proxy Candidates (constructible from census data)

These could be engineered from existing features without new labels:

| Candidate | Construction | Rationale |
|-----------|-------------|-----------|
| **Composite affluence score** | Weighted combination: income label + capital gains + dividends + wage per hour | Captures multiple wealth dimensions, not just income bracket |
| **Financial-activity indicator** | Binary: any nonzero capital gains OR dividends OR high wage | Indicates investment behavior, stronger premium-product signal |
| **Household economic capacity** | Income label + tax filer status + household role + weeks worked | Combines earning potential with household economics |
| **Employment quality index** | Occupation code + industry + self-employment + weeks worked | Proxies career-stage earning trajectory |

**Status**: Design-only. These would require new target engineering and model retraining in Phase 2.

### Tier 2: Better Business Targets (require external data)

If a real retail client provided business data, these would be superior:

| Target | What It Measures | Why It's Better |
|--------|-----------------|-----------------|
| **Response propensity** | P(responds to offer) | Directly optimizes marketing ROI |
| **Conversion rate** | P(opens account / buys product) | Measures actual business outcome |
| **Premium product uptake** | P(selects premium tier) | Targets the specific revenue action |
| **Customer lifetime value (CLV)** | Expected revenue over N years | Optimizes long-term portfolio value |
| **Churn propensity** (for retention) | P(leaves within 12 months) | Retention-focused variant |

**Status**: Not available in census data. Documented as the production-grade direction.

### Tier 3: Ideal Targeting Framework (full production)

In a mature production system, targeting would combine:
- **Propensity model**: P(response | features) — who will engage
- **Value model**: E[revenue | response] — how much they're worth
- **Expected value**: P(response) × E[revenue] — optimal budget allocation

The V1 income proxy approximates the value model component. The propensity component is entirely missing from census data.

## 4. What V2 Can Actually Do

Given that only census data is available, V2's realistic improvements are:

1. **Frame the target hierarchy explicitly** (this document) — done
2. **Design Tier 1 upgraded proxies** — constructible, experimental
3. **Build score-band analysis** that treats the V1 score as a continuous targeting dimension rather than a binary label — Phase 2
4. **Demonstrate the target-upgrade path** so a real client engagement could plug in Tier 2/3 targets without rebuilding the entire pipeline

## 5. Recommendations

| Priority | Action | Phase |
|----------|--------|-------|
| High | Use V1 binary target as Tier 0 baseline | Done (V1) |
| Medium | Prototype a composite affluence indicator (Tier 1) | Phase 2 |
| Medium | Build score-band analysis to exploit the continuous score | Phase 2 |
| Low (design) | Document Tier 2/3 target path for production readiness | Done (this doc) |
| N/A | Build response/CLV model | Requires external data |

## 6. Key Principle

> The target defines the ceiling. A perfect model trained on a weak proxy will never be as useful as a decent model trained on the right business outcome.

V1's classifier is strong (PR-AUC 0.70). The biggest improvement opportunity is not better algorithms — it's better targets.
