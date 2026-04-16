# Dataset Profile Report

**Source**: `census_bureau.jsonl`  
**Rows**: 199,523  
**Columns**: 42

## Label Distribution (Raw Counts)

| Label | Count | % |
|-------|------:|--:|
| `- 50000.` | 187,141 | 93.8% |
| `50000+.` | 12,382 | 6.2% |

## Label Distribution (Weighted)

| Label | Weighted Sum | Weighted % |
|-------|-------------:|-----------:|
| `- 50000.` | 325,004,647.22 | 93.6% |
| `50000+.` | 22,241,245.25 | 6.4% |

## Year Distribution

| Year | Count | % |
|------|------:|--:|
| 94 | 99,827 | 50.0% |
| 95 | 99,696 | 50.0% |

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
- **Parseable numeric**: 199,523
- **Min**: 0.00
- **Mean**: 34.49
- **Max**: 90.00

### class of worker
- **Type**: categorical_like
- **Missing-like**: 100,245 (50.2%)
- **Unique values**: 9
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe | 100,245 |
  | Private | 72,028 |
  | Self-employed-not incorporated | 8,445 |
  | Local government | 7,784 |
  | State government | 4,227 |
  | Self-employed-incorporated | 3,265 |
  | Federal government | 2,925 |
  | Never worked | 439 |
  | Without pay | 165 |

### detailed industry recode
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 199,523
- **Min**: 0.00
- **Mean**: 15.35
- **Max**: 51.00

### detailed occupation recode
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 199,523
- **Min**: 0.00
- **Mean**: 11.31
- **Max**: 46.00

### education
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 17
- **Top values**:

  | Value | Count |
  |-------|------:|
  | High school graduate | 48,407 |
  | Children | 47,422 |
  | Some college but no degree | 27,820 |
  | Bachelors degree(BA AB BS) | 19,865 |
  | 7th and 8th grade | 8,007 |
  | 10th grade | 7,557 |
  | 11th grade | 6,876 |
  | Masters degree(MA MS MEng MEd MSW MBA) | 6,541 |
  | 9th grade | 6,230 |
  | Associates degree-occup /vocational | 5,358 |

### wage per hour
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 199,523
- **Min**: 0.00
- **Mean**: 55.43
- **Max**: 9,999.00

### enroll in edu inst last wk
- **Type**: categorical_like
- **Missing-like**: 186,943 (93.7%)
- **Unique values**: 3
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe | 186,943 |
  | High school | 6,892 |
  | College or university | 5,688 |

### marital stat
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 7
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Never married | 86,485 |
  | Married-civilian spouse present | 84,222 |
  | Divorced | 12,710 |
  | Widowed | 10,463 |
  | Separated | 3,460 |
  | Married-spouse absent | 1,518 |
  | Married-A F spouse present | 665 |

### major industry code
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 24
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe or children | 100,684 |
  | Retail trade | 17,070 |
  | Manufacturing-durable goods | 9,015 |
  | Education | 8,283 |
  | Manufacturing-nondurable goods | 6,897 |
  | Finance insurance and real estate | 6,145 |
  | Construction | 5,984 |
  | Business and repair services | 5,651 |
  | Medical except hospital | 4,683 |
  | Public administration | 4,610 |

### major occupation code
- **Type**: categorical_like
- **Missing-like**: 100,684 (50.5%)
- **Unique values**: 15
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe | 100,684 |
  | Adm support including clerical | 14,837 |
  | Professional specialty | 13,940 |
  | Executive admin and managerial | 12,495 |
  | Other service | 12,099 |
  | Sales | 11,783 |
  | Precision production craft & repair | 10,518 |
  | Machine operators assmblrs & inspctrs | 6,379 |
  | Handlers equip cleaners etc | 4,127 |
  | Transportation and material moving | 4,020 |

### race
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 5
- **Top values**:

  | Value | Count |
  |-------|------:|
  | White | 167,365 |
  | Black | 20,415 |
  | Asian or Pacific Islander | 5,835 |
  | Other | 3,657 |
  | Amer Indian Aleut or Eskimo | 2,251 |

### hispanic origin
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 10
- **Top values**:

  | Value | Count |
  |-------|------:|
  | All other | 171,907 |
  | Mexican-American | 8,079 |
  | Mexican (Mexicano) | 7,234 |
  | Central or South American | 3,895 |
  | Puerto Rican | 3,313 |
  | Other Spanish | 2,485 |
  | Cuban | 1,126 |
  | NA | 874 |
  | Do not know | 306 |
  | Chicano | 304 |

### sex
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 2
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Female | 103,984 |
  | Male | 95,539 |

### member of a labor union
- **Type**: categorical_like
- **Missing-like**: 180,459 (90.4%)
- **Unique values**: 3
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe | 180,459 |
  | No | 16,034 |
  | Yes | 3,030 |

### reason for unemployment
- **Type**: categorical_like
- **Missing-like**: 193,453 (97.0%)
- **Unique values**: 6
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe | 193,453 |
  | Other job loser | 2,038 |
  | Re-entrant | 2,019 |
  | Job loser - on layoff | 976 |
  | Job leaver | 598 |
  | New entrant | 439 |

### full or part time employment stat
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 8
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Children or Armed Forces | 123,769 |
  | Full-time schedules | 40,736 |
  | Not in labor force | 26,808 |
  | PT for non-econ reasons usually FT | 3,322 |
  | Unemployed full-time | 2,311 |
  | PT for econ reasons usually PT | 1,209 |
  | Unemployed part- time | 843 |
  | PT for econ reasons usually FT | 525 |

### capital gains
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 199,523
- **Min**: 0.00
- **Mean**: 434.72
- **Max**: 99,999.00

### capital losses
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 199,523
- **Min**: 0.00
- **Mean**: 37.31
- **Max**: 4,608.00

### dividends from stocks
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 199,523
- **Min**: 0.00
- **Mean**: 197.53
- **Max**: 99,999.00

### tax filer stat
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 6
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Nonfiler | 75,094 |
  | Joint both under 65 | 67,383 |
  | Single | 37,421 |
  | Joint both 65+ | 8,332 |
  | Head of household | 7,426 |
  | Joint one under 65 & one 65+ | 3,867 |

### region of previous residence
- **Type**: categorical_like
- **Missing-like**: 183,750 (92.1%)
- **Unique values**: 6
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe | 183,750 |
  | South | 4,889 |
  | West | 4,074 |
  | Midwest | 3,575 |
  | Northeast | 2,705 |
  | Abroad | 530 |

### state of previous residence
- **Type**: categorical_like
- **Missing-like**: 184,458 (92.4%)
- **Unique values**: 51
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe | 183,750 |
  | California | 1,714 |
  | Utah | 1,063 |
  | Florida | 849 |
  | North Carolina | 812 |
  | ? | 708 |
  | Abroad | 671 |
  | Oklahoma | 626 |
  | Minnesota | 576 |
  | Indiana | 533 |

### detailed household and family stat
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 38
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Householder | 53,248 |
  | Child <18 never marr not in subfamily | 50,326 |
  | Spouse of householder | 41,695 |
  | Nonfamily householder | 22,213 |
  | Child 18+ never marr Not in a subfamily | 12,030 |
  | Secondary individual | 6,122 |
  | Other Rel 18+ ever marr not in subfamily | 1,956 |
  | Grandchild <18 never marr child of subfamily RP | 1,868 |
  | Other Rel 18+ never marr not in subfamily | 1,728 |
  | Grandchild <18 never marr not in subfamily | 1,066 |

### detailed household summary in household
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 8
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Householder | 75,475 |
  | Child under 18 never married | 50,426 |
  | Spouse of householder | 41,709 |
  | Child 18 or older | 14,430 |
  | Other relative of householder | 9,703 |
  | Nonrelative of householder | 7,601 |
  | Group Quarters- Secondary individual | 132 |
  | Child under 18 ever married | 47 |

### weight
- **Type**: numeric_weight
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 199,523
- **Min**: 37.87
- **Mean**: 1,740.38
- **Max**: 18,656.30

### migration code-change in msa
- **Type**: categorical_like
- **Missing-like**: 101,212 (50.7%)
- **Unique values**: 10
- **Top values**:

  | Value | Count |
  |-------|------:|
  | ? | 99,696 |
  | Nonmover | 82,538 |
  | MSA to MSA | 10,601 |
  | NonMSA to nonMSA | 2,811 |
  | Not in universe | 1,516 |
  | MSA to nonMSA | 790 |
  | NonMSA to MSA | 615 |
  | Abroad to MSA | 453 |
  | Not identifiable | 430 |
  | Abroad to nonMSA | 73 |

### migration code-change in reg
- **Type**: categorical_like
- **Missing-like**: 101,212 (50.7%)
- **Unique values**: 9
- **Top values**:

  | Value | Count |
  |-------|------:|
  | ? | 99,696 |
  | Nonmover | 82,538 |
  | Same county | 9,812 |
  | Different county same state | 2,797 |
  | Not in universe | 1,516 |
  | Different region | 1,178 |
  | Different state same division | 991 |
  | Abroad | 530 |
  | Different division same region | 465 |

### migration code-move within reg
- **Type**: categorical_like
- **Missing-like**: 101,212 (50.7%)
- **Unique values**: 10
- **Top values**:

  | Value | Count |
  |-------|------:|
  | ? | 99,696 |
  | Nonmover | 82,538 |
  | Same county | 9,812 |
  | Different county same state | 2,797 |
  | Not in universe | 1,516 |
  | Different state in South | 973 |
  | Different state in West | 679 |
  | Different state in Midwest | 551 |
  | Abroad | 530 |
  | Different state in Northeast | 431 |

### live in this house 1 year ago
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 3
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe under 1 year old | 101,212 |
  | Yes | 82,538 |
  | No | 15,773 |

### migration prev res in sunbelt
- **Type**: categorical_like
- **Missing-like**: 183,750 (92.1%)
- **Unique values**: 4
- **Top values**:

  | Value | Count |
  |-------|------:|
  | ? | 99,696 |
  | Not in universe | 84,054 |
  | No | 9,987 |
  | Yes | 5,786 |

### num persons worked for employer
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 199,523
- **Min**: 0.00
- **Mean**: 1.96
- **Max**: 6.00

### family members under 18
- **Type**: categorical_like
- **Missing-like**: 144,232 (72.3%)
- **Unique values**: 5
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe | 144,232 |
  | Both parents present | 38,983 |
  | Mother only present | 12,772 |
  | Father only present | 1,883 |
  | Neither parent present | 1,653 |

### country of birth father
- **Type**: categorical_like
- **Missing-like**: 6,713 (3.4%)
- **Unique values**: 43
- **Top values**:

  | Value | Count |
  |-------|------:|
  | United-States | 159,163 |
  | Mexico | 10,008 |
  | ? | 6,713 |
  | Puerto-Rico | 2,680 |
  | Italy | 2,212 |
  | Canada | 1,380 |
  | Germany | 1,356 |
  | Dominican-Republic | 1,290 |
  | Poland | 1,212 |
  | Philippines | 1,154 |

### country of birth mother
- **Type**: categorical_like
- **Missing-like**: 6,119 (3.1%)
- **Unique values**: 43
- **Top values**:

  | Value | Count |
  |-------|------:|
  | United-States | 160,479 |
  | Mexico | 9,781 |
  | ? | 6,119 |
  | Puerto-Rico | 2,473 |
  | Italy | 1,844 |
  | Canada | 1,451 |
  | Germany | 1,382 |
  | Philippines | 1,231 |
  | Poland | 1,110 |
  | El-Salvador | 1,108 |

### country of birth self
- **Type**: categorical_like
- **Missing-like**: 3,393 (1.7%)
- **Unique values**: 43
- **Top values**:

  | Value | Count |
  |-------|------:|
  | United-States | 176,989 |
  | Mexico | 5,767 |
  | ? | 3,393 |
  | Puerto-Rico | 1,400 |
  | Germany | 851 |
  | Philippines | 845 |
  | Cuba | 837 |
  | Canada | 700 |
  | Dominican-Republic | 690 |
  | El-Salvador | 689 |

### citizenship
- **Type**: categorical_like
- **Missing-like**: 0 (0.0%)
- **Unique values**: 5
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Native- Born in the United States | 176,992 |
  | Foreign born- Not a citizen of U S | 13,401 |
  | Foreign born- U S citizen by naturalization | 5,855 |
  | Native- Born abroad of American Parent(s) | 1,756 |
  | Native- Born in Puerto Rico or U S Outlying | 1,519 |

### own business or self employed
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 199,523
- **Min**: 0.00
- **Mean**: 0.18
- **Max**: 2.00

### fill inc questionnaire for veteran's admin
- **Type**: categorical_like
- **Missing-like**: 197,539 (99.0%)
- **Unique values**: 3
- **Top values**:

  | Value | Count |
  |-------|------:|
  | Not in universe | 197,539 |
  | No | 1,593 |
  | Yes | 391 |

### veterans benefits
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 199,523
- **Min**: 0.00
- **Mean**: 1.51
- **Max**: 2.00

### weeks worked in year
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 199,523
- **Min**: 0.00
- **Mean**: 23.17
- **Max**: 52.00

### year
- **Type**: numeric_like
- **Missing-like**: 0 (0.0%)
- **Parseable numeric**: 199,523
- **Min**: 94.00
- **Mean**: 94.50
- **Max**: 95.00

### label
- **Type**: target_categorical
- **Missing-like**: 0 (0.0%)
- **Unique values**: 2
- **Top values**:

  | Value | Count |
  |-------|------:|
  | - 50000. | 187,141 |
  | 50000+. | 12,382 |

---

## Interpretation Notes

1. **Sample vs. population**: If this report was run on a sample file, raw proportions may not match the full dataset. Do not treat sample counts as population-representative.
2. **Weight column**: The `weight` column represents CPS population weights. Final model evaluation and any business-facing metrics (e.g., weighted accuracy, segment sizes) should incorporate these weights.
3. **Sentinel values**: Values like `?`, `Not in universe`, and empty strings appear frequently and require deliberate preprocessing decisions (drop, impute, or encode as a separate category) depending on the column and modeling approach.
4. **Label encoding**: The target labels `- 50000.` and `50000+.` should be mapped to binary 0/1 for classification.
5. **Year variable**: Two survey years (94/95) are present. Consider whether to stratify, feature-engineer, or simply include as a covariate.
