# Exact Second-Pass Sub-Segment Profiles

> Status: **Empirical result on exact V1 Segment 2** — see adoption decision in `segment2_exact_adoption_decision.md`

## Summary

| Sub-Seg | Name | N | % of Seg 2 | >50K | Enrichment |
|---------|------|----:|----------:|-----:|-----------:|
| 0 | Established Mid-Career Earners | 34,904 | 38.2% | 20.7% | 1.65x |
| 1 | Lower-Income Service Workers | 10,239 | 11.2% | 2.4% | 0.19x |
| 2 | Younger Mainstream Workers | 46,300 | 50.6% | 8.6% | 0.69x |

## Sub-Segment 0: Established Mid-Career Earners

- **Age**: Mean 51.5, median 50
- **Education**: HS grad 33%, some college 18%, bachelor's 17%
- **Marital**: Married 74%, divorced 13%
- **Sex**: Male 55%, female 45%
- **Occupation**: Exec/managerial 19%, professional 16%, admin 13%
- **>50K rate**: 20.66% (1.65x vs Seg 2 average)

**Marketing fit**: The primary premium-targeting group within working-age. Older, more established, highest income concentration. Investment, retirement planning, wealth management products.

## Sub-Segment 1: Lower-Income Service Workers

- **Age**: Mean 33.6, median 33
- **Education**: HS grad 35%, some college 22%, bachelor's 14%
- **Marital**: Married 54%, never married 32%
- **Sex**: Female 56%, male 44%
- **Occupation**: Other service 17%, admin 15%, professional 13%
- **>50K rate**: 2.39% (0.19x vs Seg 2 average)

**Marketing fit**: Low income-targeting value. Accessible financial products, basic banking. The income rate is similar to the senior macro segment — direct premium targeting is not productive.

## Sub-Segment 2: Younger Mainstream Workers

- **Age**: Mean 31.1, median 32
- **Education**: HS grad 34%, some college 22%, bachelor's 18%
- **Marital**: Married 55%, never married 33%
- **Sex**: Male 55%, female 45%
- **Occupation**: Admin 17%, professional 13%, precision production 11%
- **>50K rate**: 8.61% (0.69x vs Seg 2 average)

**Marketing fit**: Mid-tier. Some premium potential (bachelor's 18%, professional occupations represented). Career-stage products, mortgage, starter investment. The classifier score provides sub-targeting within this group.

## Full V2 Two-Layer Architecture (with exact lineage)

```
Population (199,523)
  ├── Seg 0: Seniors (40,618, 20.4%)      → retirement products
  ├── Seg 1: Youth (67,462, 33.8%)        → family-indirect
  └── Seg 2: Working-Age (91,443, 45.8%)
        ├── Sub-0: Established Earners (34,904, 38%)  → premium targeting
        ├── Sub-1: Service Workers (10,239, 11%)       → accessible products
        └── Sub-2: Younger Workers (46,300, 51%)       → mid-tier / growth
```
