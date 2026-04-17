# Segmentation Feature Scorecard

> Status: **Completed design artifact**

## Scoring Rubric

| Criterion | Weight | Scale |
|-----------|--------|-------|
| Business relevance | High | 1-3 (3=directly actionable) |
| Cardinality burden | Medium | 1-3 (3=low cardinality, good) |
| Sentinel burden | Medium | 1-3 (3=low sentinel %, good) |
| Redundancy | Medium | 1-3 (3=unique signal) |
| Actionability | High | 1-3 (3=business can act on it) |

## Feature Scores (Second-Pass, Working-Age Segment)

| Feature | Type | Biz Rel | Card | Sent | Redund | Action | Total | Include? |
|---------|------|--------:|-----:|-----:|-------:|-------:|------:|----------|
| age | cont | 3 | 3 | 3 | 3 | 3 | **15** | Yes |
| weeks worked in year | cont | 3 | 3 | 3 | 3 | 2 | **14** | Yes |
| education | cat | 3 | 2 | 3 | 3 | 3 | **14** | Yes |
| major occupation code | cat | 3 | 2 | 2 | 2 | 3 | **12** | Yes |
| class of worker | cat | 3 | 3 | 2 | 2 | 3 | **13** | Yes |
| tax filer stat | cat | 3 | 3 | 3 | 2 | 2 | **13** | Yes |
| capital gains | cont | 2 | 3 | 3 | 2 | 2 | **12** | Yes |
| dividends from stocks | cont | 2 | 3 | 3 | 2 | 2 | **12** | Yes |
| wage per hour | cont | 2 | 3 | 3 | 2 | 2 | **12** | Yes |
| marital stat | cat | 2 | 3 | 3 | 2 | 2 | **12** | Yes |
| sex | cat | 2 | 3 | 3 | 2 | 2 | **12** | Yes |
| major industry code | cat | 2 | 1 | 2 | 2 | 2 | **9** | Yes |
| own business or self employed | cat | 2 | 3 | 3 | 1 | 2 | **11** | Yes |
| detailed household summary | cat | 2 | 3 | 3 | 1 | 2 | **11** | Yes |
| family members under 18 | cat | 2 | 3 | 1 | 2 | 2 | **10** | No* |
| citizenship | cat | 1 | 3 | 3 | 2 | 1 | **10** | No* |
| detailed industry recode | cat | 1 | 1 | 3 | 1 | 1 | **7** | No |
| detailed occupation recode | cat | 1 | 1 | 3 | 1 | 1 | **7** | No |
| veterans benefits | cat | 1 | 3 | 3 | 2 | 1 | **10** | No |

*family members under 18: excluded because 99% "Not in universe" within working-age segment (no variation). citizenship: excluded because 87% native-born (low variation).*

## Final Feature Set

**14 features**: 5 continuous + 9 categorical (see `segment2_second_pass_design.md` for the full list).

## Comparison: V1 vs V2 Feature Selection

| Aspect | V1 (macro) | V2 (second-pass) |
|--------|-----------|------------------|
| Population | Full 199,523 | Working-age ~92,000 |
| Features | 17 (5 cont + 12 cat) | 14 (5 cont + 9 cat) |
| Family under 18 | Included (variation across life-stages) | Excluded (no variation within working-age) |
| Citizenship | Included | Excluded (low variation) |
| Live in house 1 yr ago | Included | Excluded (low actionability for sub-segmentation) |
