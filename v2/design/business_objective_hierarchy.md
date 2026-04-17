# Business Objective Hierarchy

> Status: **Completed design artifact** (Phase 1 closure)

## The Hierarchy

```
Tier 3: Ideal Production Framework
  E[value] = P(response) x E[revenue | response]
  Requires: transaction data, response logs, revenue attribution
  Status: Future — requires real client engagement
        |
Tier 2: Better Business Targets
  Response propensity, conversion, CLV, premium uptake
  Requires: campaign outcome data
  Status: Future — unavailable in census data
        |
Tier 1: Upgraded Proxy Candidates
  Composite affluence, financial-activity indicator
  Requires: feature engineering on existing census data
  Status: Constructible — V2 design phase
        |
Tier 0: V1 Baseline Proxy (current)
  Binary: income > $50K
  Available now; PR-AUC 0.70 on test
```

## Tier Definitions

### Tier 0 — Current V1 Proxy
**Target**: Income > $50K (binary)
**What it measures**: Whether the CPS income variable exceeds a round threshold in 1994 dollars
**Strengths**: Simple, available, strong classification performance (ROC-AUC 0.96)
**Weaknesses**: Binary at an arbitrary cut, ignores wealth/assets, 1994 dollars, no behavioral signal

### Tier 1 — Upgraded Proxy Candidates
**What they are**: Composite targets constructible from existing census features
**Strengths**: Richer than single binary; capture multiple wealth dimensions
**Weaknesses**: Still no behavioral/response data; still proxies
**Status**: Designed in `proxy_target_upgrade_options.md`; execution is optional Phase 2

### Tier 2 — Better Business Targets
**What they are**: Targets derived from actual business outcomes
**Examples**: P(responds to offer), P(converts to premium product), expected CLV
**Strengths**: Directly optimize business value
**Weaknesses**: Require data the census doesn't provide
**Status**: Documented as production direction; not buildable now

### Tier 3 — Ideal Production Framework
**What it is**: Expected-value targeting: contact if P(response) x E[revenue] > cost
**Strengths**: Optimal budget allocation under known economics
**Weaknesses**: Requires response model + value model + cost model
**Status**: Documented as gold standard; fully future work

## Key Principle

Each tier up represents better alignment between what the model optimizes and what the business actually wants. V1's Tier 0 target is a useful starting point. The biggest leverage for V2+ is moving up the hierarchy, not squeezing more performance from the existing proxy.
