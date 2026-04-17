# V2 Final Acceptance Note

## Final Accepted Architecture

### Classifier
- **Model**: CatBoost (depth=6, lr=0.08, l2_leaf_reg=1.0)
- **Features**: Reduced set (31 features)
- **Training**: Unweighted (survey-weighted variants tested, not adopted)
- **Evaluation**: Both unweighted and survey-weighted
- **Test PR-AUC**: 0.7008 | ROC-AUC: 0.9565 | F1 @0.25: 0.6276

### Threshold / Decision Policy
- Balanced: 0.25 | Precision-leaning: 0.45 | Recall-leaning: 0.20
- Score-band framework (A through E) with empirical cumulative capture
- Budget/capacity-aware decision logic with explicit economic assumptions

### Macro Segmentation (V1, frozen)
- 3 segments: Seniors (20%), Youth (34%), Working-Age (46%)
- K-Prototypes, exact labels recovered and verified

### Layer 2 Micro-Segmentation (V2, conditionally adopted)
- 3 sub-segments within Working-Age on exact V1 Segment 2 population:
  - Established Mid-Career Earners (38%, 20.7% >50K)
  - Lower-Income Service Workers (11%, 2.4% >50K)
  - Younger Mainstream Workers (51%, 8.6% >50K)
- Multi-seed stability: 3/4 seeds produce 3 sub-segments; service-worker group most stable
- Condition: directional, not precise boundaries

### Governance
- Weight never used as feature or training weight
- Target excluded from clustering input
- Fairness note documents demographic feature sensitivity
- Segment-conditioned diagnostics (rules-based macro assignment) show classifier quality varies by segment

## What Was Tested and Not Adopted

| Extension | Why Not Adopted |
|-----------|----------------|
| Survey-weighted training (3 variants) | All underperformed unweighted baseline |
| LightGBM | -0.009 PR-AUC vs CatBoost |
| XGBoost | -0.010 PR-AUC vs CatBoost |

## What Remains Out of Scope

- Real campaign response/conversion data (Tier 2+ targets)
- Production deployment pipeline
- Full fairness impact assessment
- Current-year data refresh
- Exploratory broad-feature segmentation track
