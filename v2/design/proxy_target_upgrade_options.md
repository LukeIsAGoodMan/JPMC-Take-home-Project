# Proxy Target Upgrade Options

> Status: **Completed design artifact** (Phase 1 closure)

These are Tier 1 targets — constructible from existing census features, better than raw >$50K, but still proxies.

## Option 1: Financial Activity Indicator

**Definition**: Binary flag = 1 if any of: capital_gains > 0, dividends > 0, wage_per_hour > median

**What it captures**: Investment behavior and above-median earning rate — signals financial engagement beyond just income bracket

**Advantages over V1 target**:
- Captures wealth accumulation, not just income threshold
- Individuals with capital gains/dividends are more likely premium-product candidates regardless of income level

**Executable now?** Yes — all features available in census data

**Risk**: May have high correlation with existing V1 target; marginal improvement uncertain without testing

## Option 2: Composite Affluence Score

**Definition**: Weighted sum: 0.4 x income_label + 0.2 x norm(capital_gains) + 0.2 x norm(dividends) + 0.1 x norm(wage_per_hour) + 0.1 x norm(weeks_worked)

**What it captures**: Multi-dimensional economic strength across income, investment, and labor attachment

**Advantages over V1 target**:
- Continuous rather than binary — enables richer ranking
- Incorporates wealth proxies alongside income

**Executable now?** Yes, but requires defining normalization and weight choices (introduces subjectivity)

**Risk**: Weight choices are arbitrary without outcome data to calibrate against

## Option 3: Household Economic Capacity

**Definition**: Composite based on income_label + tax_filer_stat + household_role + weeks_worked

**What it captures**: Household-level economic position, not just individual income

**Advantages over V1 target**:
- A married joint-filer householder working 52 weeks is economically different from a single part-time worker, even at the same income level
- More relevant for household-oriented financial products

**Executable now?** Yes — all features available; requires encoding choices for categorical inputs

**Risk**: Mixing categorical and numeric signals into one index requires design decisions

## Option 4: Employment Quality Index

**Definition**: Derived from occupation_code + industry_code + self_employment_flag + weeks_worked + education

**What it captures**: Career-stage earning trajectory — someone in a professional specialty with a bachelor's degree and 52 weeks worked is on a different trajectory than a retail worker

**Advantages over V1 target**:
- Forward-looking (earning trajectory) vs backward-looking (current income bracket)
- Better for targeting young professionals who will become high-value

**Executable now?** Partially — requires ordinal encoding of occupation quality, which is subjective

**Risk**: Occupation quality ranking is a human judgment, not a data-derived fact

## Summary

| Option | Executable Now | Data Required | Key Advantage | Key Risk |
|--------|---------------|--------------|---------------|----------|
| Financial Activity Indicator | Yes | Census features | Captures wealth beyond income | Correlation with V1 target |
| Composite Affluence Score | Yes (with design choices) | Census features | Continuous, multi-dimensional | Arbitrary weights |
| Household Economic Capacity | Yes (with encoding) | Census features | Household-level signal | Complex encoding |
| Employment Quality Index | Partially | Census + judgment | Trajectory-aware | Subjective quality ranking |

## Recommendation

**Option 1 (Financial Activity Indicator)** is the safest first upgrade: it's binary, simple, executable immediately, and captures a genuinely different signal (wealth/investment behavior) vs the raw income proxy.

If the goal is a richer continuous score, **Option 2 (Composite Affluence)** is worth prototyping, but its arbitrary weight choices should be tested against downstream utility rather than assumed.

**None of these replace Tier 2/3 targets.** They are incremental improvements within the census-data constraint.
