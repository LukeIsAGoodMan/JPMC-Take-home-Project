# EDA Summary

> Derived from: datasource/summary_report_full.md, pipeline/outputs/PREPROCESSING_AUDIT.md, TECHNICAL_APPENDIX.md

## Dataset Overview

| Attribute | Value |
|-----------|-------|
| Source | Current Population Survey (CPS), 1994-1995 |
| Records | 199,523 |
| Columns | 42 |
| Target | Binary income: `- 50000.` (0) vs `50000+.` (1) |
| Survey years | 94 (50.0%), 95 (50.0%) |

## Target Imbalance

| Class | Count | % |
|-------|------:|--:|
| <= $50K | 187,141 | 93.8% |
| > $50K | 12,382 | 6.2% |

The positive class is rare. A naive "predict everyone as <=50K" achieves 93.8% accuracy — making accuracy a misleading metric. PR-AUC is the primary evaluation criterion.

## Feature Types

| Type | Count | Examples |
|------|------:|---------|
| Continuous numeric | 7 | age, wage per hour, capital gains, weeks worked in year |
| Numeric-coded categorical | 5 | detailed industry recode (0-51), veterans benefits (0-2), year (94/95) |
| Text categorical | 28 | education, marital stat, major occupation code |
| Sample weight | 1 | weight (range 38-18,656) |
| Target | 1 | label |

## Sentinel / Missing Structure

| Pattern | Prevalence | Treatment |
|---------|-----------|-----------|
| `Not in universe` | 15+ columns, 50-99% of rows | Preserved as explicit category — encodes life-stage |
| `?` | 6 columns, 1-50% | Mapped to `Unknown` — ambiguity signal |
| Empty string | Rare/none observed | Mapped to `Missing` |
| Numeric zeros | Financial columns | Preserved — valid zero-income values |

**Key insight**: `Not in universe` is NOT missing data. It indicates structural non-applicability (children, retirees, non-labor-force). Treating it as generic NA would destroy highly predictive life-stage information.

## Notable Sparsity

| Column | % Not-in-Universe / Unknown |
|--------|---------------------------:|
| fill inc questionnaire for veteran's admin | 99.0% |
| reason for unemployment | 97.0% |
| enroll in edu inst last wk | 93.7% |
| region of previous residence | 92.1% |
| member of a labor union | 90.4% |

Five of these columns were flagged as "review" columns and later confirmed to add noise, not signal — the reduced feature set outperformed full.

## Survey Weight

The `weight` column represents CPS population weights for survey-representative analysis. It ranges from 38 to 18,656 (mean 1,740).

- **Used for**: population-representative evaluation, segment sizing
- **NOT used as**: a predictive feature or training sample weight

## Key Risks Identified

1. Target imbalance (6.2%) requires imbalance-aware metrics
2. Numeric-coded columns (5) must not be treated as continuous
3. Sentinel-heavy columns require column-aware handling, not blanket imputation
4. Duplicate rows (1.6%) are expected census population patterns, not data errors
