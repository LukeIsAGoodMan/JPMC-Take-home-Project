# Dataset Profile Report

**Source**: `sample_stratified.jsonl`  
**Rows**: 200  
**Columns**: 42

## Label Distribution (Raw Counts)

| Label | Count | % |
|-------|------:|--:|
| `- 50000.` | 100 | 50.0% |
| `50000+.` | 100 | 50.0% |

## Label Distribution (Weighted)

| Label | Weighted Sum | Weighted % |
|-------|-------------:|-----------:|
| `50000+.` | 181,112.48 | 52.4% |
| `- 50000.` | 164,832.27 | 47.6% |

## Year Distribution

| Year | Count | % |
|------|------:|--:|
| 94 | 103 | 51.5% |
| 95 | 97 | 48.5% |

## Column Types

| # | Column | Inferred Type |
|---|--------|---------------|
| 1 | age | numeric_like |
| 2 | class of worker | categorical_like |
| 3 | detailed industry recode | numeric_like |
| 4 | detailed occupation recode | numeric_like |
| 5 | education | categorical_like |
| 6 | wage per hour | numeric_like |
| 7 | enroll in edu inst last wk | categorical_like |
| 8 | marital stat | categorical_like |
| 9 | major industry code | categorical_like |
| 10 | major occupation code | categorical_like |
| 11 | race | categorical_like |
| 12 | hispanic origin | categorical_like |
| 13 | sex | categorical_like |
| 14 | member of a labor union | categorical_like |
| 15 | reason for unemployment | categorical_like |
| 16 | full or part time employment stat | categorical_like |
| 17 | capital gains | numeric_like |
| 18 | capital losses | numeric_like |
| 19 | dividends from stocks | numeric_like |
| 20 | tax filer stat | categorical_like |
| 21 | region of previous residence | categorical_like |
| 22 | state of previous residence | categorical_like |
| 23 | detailed household and family stat | categorical_like |
| 24 | detailed household summary in household | categorical_like |
| 25 | weight | numeric_weight |
| 26 | migration code-change in msa | categorical_like |
| 27 | migration code-change in reg | categorical_like |
| 28 | migration code-move within reg | categorical_like |
| 29 | live in this house 1 year ago | categorical_like |
| 30 | migration prev res in sunbelt | categorical_like |
| 31 | num persons worked for employer | numeric_like |
| 32 | family members under 18 | categorical_like |
| 33 | country of birth father | categorical_like |
| 34 | country of birth mother | categorical_like |
| 35 | country of birth self | categorical_like |
| 36 | citizenship | categorical_like |
| 37 | own business or self employed | numeric_like |
| 38 | fill inc questionnaire for veteran's admin | categorical_like |
| 39 | veterans benefits | numeric_like |
| 40 | weeks worked in year | numeric_like |
| 41 | year | numeric_like |
| 42 | label | target_categorical |

## Per-Column Profile

### age
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 200
- **Min**: 0.00
- **Mean**: 39.75
- **Max**: 85.00

### class of worker
- **Type**: categorical_like
- **Missing-like**: 62 (31.0%)
- **Unique values**: 7
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Private | 94 |
  | Not in universe | 62 |
  | Self-employed-not incorporated | 15 |
  | Local government | 10 |
  | Self-employed-incorporated | 7 |
  | Federal government | 6 |
  | State government | 6 |

### detailed industry recode
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 200
- **Min**: 0.00
- **Mean**: 21.89
- **Max**: 50.00

### detailed occupation recode
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 200
- **Min**: 0.00
- **Mean**: 12.07
- **Max**: 45.00

### education
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 15
- **Top values**:

  | Value | Count |
  |-------|------:|
  | High school graduate | 44 |
  | Bachelors degree(BA AB BS) | 39 |
  | Children | 31 |
  | Some college but no degree | 24 |
  | Masters degree(MA MS MEng MEd MSW MBA) | 16 |
  | Prof school degree (MD DDS DVM LLB JD) | 9 |
  | Doctorate degree(PhD EdD) | 8 |
  | Associates degree-academic program | 7 |
  | 7th and 8th grade | 6 |
  | Associates degree-occup /vocational | 5 |

### wage per hour
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 200
- **Min**: 0.00
- **Mean**: 110.44
- **Max**: 2,250.00

### enroll in edu inst last wk
- **Type**: categorical_like
- **Missing-like**: 195 (97.5%)
- **Unique values**: 3
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe | 195 |
  | High school | 4 |
  | College or university | 1 |

### marital stat
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 6
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Married-civilian spouse present | 102 |
  | Never married | 67 |
  | Divorced | 14 |
  | Widowed | 11 |
  | Separated | 4 |
  | Married-spouse absent | 2 |

### major industry code
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 22
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe or children | 62 |
  | Manufacturing-durable goods | 17 |
  | Retail trade | 14 |
  | Education | 13 |
  | Other professional services | 9 |
  | Medical except hospital | 9 |
  | Hospital services | 9 |
  | Construction | 8 |
  | Manufacturing-nondurable goods | 8 |
  | Finance insurance and real estate | 8 |

### major occupation code
- **Type**: categorical_like
- **Missing-like**: 62 (31.0%)
- **Unique values**: 13
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe | 62 |
  | Professional specialty | 36 |
  | Executive admin and managerial | 27 |
  | Sales | 18 |
  | Precision production craft & repair | 14 |
  | Adm support including clerical | 9 |
  | Other service | 8 |
  | Machine operators assmblrs & inspctrs | 6 |
  | Transportation and material moving | 6 |
  | Technicians and related support | 6 |

### race
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 5
- **Top values**:

  | Value | Count |
  |-------|------:|
  | White | 176 |
  | Black | 10 |
  | Asian or Pacific Islander | 9 |
  | Amer Indian Aleut or Eskimo | 3 |
  | Other | 2 |

### hispanic origin
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 7
- **Top values**:

  | Value | Count |
  |-------|------:|
  | All other | 178 |
  | Mexican-American | 8 |
  | Central or South American | 6 |
  | Mexican (Mexicano) | 4 |
  | Other Spanish | 2 |
  | Puerto Rican | 1 |
  | Do not know | 1 |

### sex
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 2
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Male | 122 |
  | Female | 78 |

### member of a labor union
- **Type**: categorical_like
- **Missing-like**: 172 (86.0%)
- **Unique values**: 3
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe | 172 |
  | No | 24 |
  | Yes | 4 |

### reason for unemployment
- **Type**: categorical_like
- **Missing-like**: 195 (97.5%)
- **Unique values**: 4
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe | 195 |
  | Re-entrant | 2 |
  | Job leaver | 2 |
  | Job loser - on layoff | 1 |

### full or part time employment stat
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 7
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Children or Armed Forces | 114 |
  | Full-time schedules | 58 |
  | Not in labor force | 17 |
  | PT for non-econ reasons usually FT | 6 |
  | PT for econ reasons usually PT | 3 |
  | Unemployed full-time | 1 |
  | PT for econ reasons usually FT | 1 |

### capital gains
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 200
- **Min**: 0.00
- **Mean**: 2,349.80
- **Max**: 99,999.00

### capital losses
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 200
- **Min**: 0.00
- **Mean**: 150.47
- **Max**: 3,683.00

### dividends from stocks
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 200
- **Min**: 0.00
- **Mean**: 873.39
- **Max**: 38,758.00

### tax filer stat
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 6
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Joint both under 65 | 90 |
  | Nonfiler | 41 |
  | Single | 41 |
  | Head of household | 17 |
  | Joint both 65+ | 8 |
  | Joint one under 65 & one 65+ | 3 |

### region of previous residence
- **Type**: categorical_like
- **Missing-like**: 183 (91.5%)
- **Unique values**: 5
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe | 183 |
  | West | 6 |
  | South | 6 |
  | Midwest | 3 |
  | Northeast | 2 |

### state of previous residence
- **Type**: categorical_like
- **Missing-like**: 183 (91.5%)
- **Unique values**: 13
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe | 183 |
  | Illinois | 2 |
  | Indiana | 2 |
  | Florida | 2 |
  | District of Columbia | 2 |
  | Utah | 2 |
  | Alaska | 1 |
  | California | 1 |
  | New Hampshire | 1 |
  | Iowa | 1 |

### detailed household and family stat
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 13
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Householder | 86 |
  | Spouse of householder | 36 |
  | Child <18 never marr not in subfamily | 30 |
  | Nonfamily householder | 29 |
  | Child 18+ never marr Not in a subfamily | 6 |
  | Secondary individual | 4 |
  | Other Rel 18+ never marr not in subfamily | 3 |
  | Other Rel <18 never marr child of subfamily RP | 1 |
  | Child under 18 of RP of unrel subfamily | 1 |
  | Child 18+ never marr RP of subfamily | 1 |

### detailed household summary in household
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 6
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Householder | 115 |
  | Spouse of householder | 36 |
  | Child under 18 never married | 30 |
  | Child 18 or older | 7 |
  | Other relative of householder | 6 |
  | Nonrelative of householder | 6 |

### weight
- **Type**: numeric_weight
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 200
- **Min**: 139.88
- **Mean**: 1,729.72
- **Max**: 5,625.22

### migration code-change in msa
- **Type**: categorical_like
- **Missing-like**: 100 (50.0%)
- **Unique values**: 5
- **Top values**:

  | Value | Count |
  |-------|------:|
  | ? | 97 |
  | Nonmover | 83 |
  | MSA to MSA | 11 |
  | NonMSA to nonMSA | 6 |
  | Not in universe | 3 |

### migration code-change in reg
- **Type**: categorical_like
- **Missing-like**: 100 (50.0%)
- **Unique values**: 7
- **Top values**:

  | Value | Count |
  |-------|------:|
  | ? | 97 |
  | Nonmover | 83 |
  | Same county | 12 |
  | Not in universe | 3 |
  | Different state same division | 3 |
  | Different region | 1 |
  | Different county same state | 1 |

### migration code-move within reg
- **Type**: categorical_like
- **Missing-like**: 100 (50.0%)
- **Unique values**: 7
- **Top values**:

  | Value | Count |
  |-------|------:|
  | ? | 97 |
  | Nonmover | 83 |
  | Same county | 12 |
  | Not in universe | 3 |
  | Different state in South | 3 |
  | Different county same state | 1 |
  | Different state in West | 1 |

### live in this house 1 year ago
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 3
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe under 1 year old | 100 |
  | Yes | 83 |
  | No | 17 |

### migration prev res in sunbelt
- **Type**: categorical_like
- **Missing-like**: 183 (91.5%)
- **Unique values**: 4
- **Top values**:

  | Value | Count |
  |-------|------:|
  | ? | 97 |
  | Not in universe | 86 |
  | No | 12 |
  | Yes | 5 |

### num persons worked for employer
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 200
- **Min**: 0.00
- **Mean**: 2.92
- **Max**: 6.00

### family members under 18
- **Type**: categorical_like
- **Missing-like**: 167 (83.5%)
- **Unique values**: 4
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe | 167 |
  | Both parents present | 24 |
  | Mother only present | 7 |
  | Father only present | 2 |

### country of birth father
- **Type**: categorical_like
- **Missing-like**: 6 (3.0%)
- **Unique values**: 20
- **Top values**:

  | Value | Count |
  |-------|------:|
  | United-States | 161 |
  | Mexico | 6 |
  | ? | 6 |
  | Philippines | 5 |
  | Germany | 3 |
  | Dominican-Republic | 2 |
  | Nicaragua | 2 |
  | China | 2 |
  | Canada | 2 |
  | El-Salvador | 1 |

### country of birth mother
- **Type**: categorical_like
- **Missing-like**: 5 (2.5%)
- **Unique values**: 21
- **Top values**:

  | Value | Count |
  |-------|------:|
  | United-States | 162 |
  | Mexico | 8 |
  | Philippines | 5 |
  | ? | 5 |
  | Columbia | 2 |
  | El-Salvador | 2 |
  | Taiwan | 2 |
  | Dominican-Republic | 1 |
  | Nicaragua | 1 |
  | South Korea | 1 |

### country of birth self
- **Type**: categorical_like
- **Missing-like**: 4 (2.0%)
- **Unique values**: 16
- **Top values**:

  | Value | Count |
  |-------|------:|
  | United-States | 176 |
  | Philippines | 5 |
  | ? | 4 |
  | Mexico | 2 |
  | Taiwan | 2 |
  | Nicaragua | 1 |
  | Puerto-Rico | 1 |
  | Guatemala | 1 |
  | Peru | 1 |
  | Outlying-U S (Guam USVI etc) | 1 |

### citizenship
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 5
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Native- Born in the United States | 176 |
  | Foreign born- Not a citizen of U S | 12 |
  | Foreign born- U S citizen by naturalization | 8 |
  | Native- Born in Puerto Rico or U S Outlying | 2 |
  | Native- Born abroad of American Parent(s) | 2 |

### own business or self employed
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 200
- **Min**: 0.00
- **Mean**: 0.28
- **Max**: 2.00

### fill inc questionnaire for veteran's admin
- **Type**: categorical_like
- **Missing-like**: 197 (98.5%)
- **Unique values**: 3
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe | 197 |
  | No | 2 |
  | Yes | 1 |

### veterans benefits
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 200
- **Min**: 0.00
- **Mean**: 1.68
- **Max**: 2.00

### weeks worked in year
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 200
- **Min**: 0.00
- **Mean**: 34.80
- **Max**: 52.00

### year
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 200
- **Min**: 94.00
- **Mean**: 94.48
- **Max**: 95.00

### label
- **Type**: target_categorical
- **Missing-like**: 0 (0.0%)
- **Unique values**: 2
- **Top values**:

  | Value | Count |
  |-------|------:|
  | - 50000. | 100 |
  | 50000+. | 100 |

---

## Interpretation Notes

1. **Sample vs. population**: If this report was run on a sample file, raw proportions may not match the full dataset. Do not treat sample counts as population-representative.
2. **Weight column**: The `weight` column represents CPS population weights. Final model evaluation and any business-facing metrics (e.g., weighted accuracy, segment sizes) should incorporate these weights.
3. **Sentinel values**: Values like `?`, `Not in universe`, and empty strings appear frequently and require deliberate preprocessing decisions (drop, impute, or encode as a separate category) depending on the column and modeling approach.
4. **Label encoding**: The target labels `- 50000.` and `50000+.` should be mapped to binary 0/1 for classification.
5. **Year variable**: Two survey years (94/95) are present. Consider whether to stratify, feature-engineer, or simply include as a covariate.
