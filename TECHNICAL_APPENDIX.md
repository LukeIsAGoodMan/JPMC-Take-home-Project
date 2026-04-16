# Technical Appendix

This document provides governance-level detail on preprocessing, modeling, and segmentation decisions. It is intended for technical reviewers, model-governance auditors, and interview discussion.

## 1. Preprocessing Governance

### 1.1 Target and Weight Treatment

| Column | Role | In Features? | Treatment |
|--------|------|-------------|-----------|
| `label` | Binary target | No | Mapped: `- 50000.` -> 0, `50000+.` -> 1 |
| `weight` | CPS survey weight | No | Used for population-representative evaluation and segment sizing only |

`weight` is **never** used as a predictive feature or as a training sample weight. This is a deliberate governance decision: survey weights address population representativeness, not label imbalance. Conflating the two would be methodologically incorrect.

### 1.2 Missing / Exception / Sentinel Handling

| Pattern | Example | Treatment |
|---------|---------|-----------|
| Structural not-applicable | `Not in universe`, `Children or Armed Forces` | Preserved as explicit category — encodes life-stage information |
| Unknown / ambiguous | `?` | Mapped to `Unknown` — preserves ambiguity signal |
| True blank | (rare/none observed) | Mapped to `Missing` in categoricals, NaN in numerics |
| Numeric outliers | `wage per hour` max=9999 | Raw values kept for trees; log1p copies for linear models |

The decision to **preserve sentinel values as categories** rather than impute them is critical. `Not in universe` in fields like `major occupation code` (50.5% of data) or `member of a labor union` (90.4%) signals that the person is not in the labor force — this is highly predictive of income and should not be collapsed into generic missingness.

### 1.3 Numeric-Coded Categorical Protection

Five columns are stored as integers but are semantic codes, not continuous measurements:

| Column | Range | Treatment |
|--------|-------|-----------|
| `detailed industry recode` | 0-51 | Cast to string category |
| `detailed occupation recode` | 0-46 | Cast to string category |
| `own business or self employed` | 0-2 | Cast to string category |
| `veterans benefits` | 0-2 | Cast to string category |
| `year` | 94-95 | Cast to string category |

Treating these as continuous would allow the model to compute means, differences, and scaling on values that have no numeric ordering — a common data-quality failure mode.

### 1.4 Train / Validation / Test Split

| Split | Rows | % | Target Rate |
|-------|-----:|--:|------------|
| Train | 139,665 | 70% | 6.21% |
| Validation | 29,929 | 15% | 6.20% |
| Test | 29,929 | 15% | 6.20% |

- Stratified on target
- Year distribution balanced across splits (~50/50)
- All encoders, scalers, and transforms fit on train only
- Seed: 42

### 1.5 Duplicate Leakage Audit

- 1.6% exact duplicate rows within the dataset (expected in census microdata)
- 6,733 shared feature vectors across splits — population duplicates, not data leakage
- 89 feature groups with conflicting targets (same demographics, different income) — proves these are different individuals
- Risk: LOW-MODERATE. No rows removed.

## 2. Classification Track

### 2.1 Stage 5: Baseline Comparison

8-configuration grid: 2 model families x 2 feature sets x 2 training modes.

| Config | PR-AUC | ROC-AUC |
|--------|-------:|--------:|
| LR/Full/NoClsBal | 0.5978 | 0.9416 |
| LR/Full/ClsBal | 0.5900 | 0.9412 |
| CB/Full/NoClsBal | 0.6865 | 0.9519 |
| CB/Red/NoClsBal | **0.6877** | 0.9517 |
| CB/Red/ClsBal | 0.6735 | 0.9523 |

**Key findings**:
- CatBoost outperformed Logistic Regression by +0.09 PR-AUC
- Reduced feature set matched or exceeded Full (5 sparse review columns add noise)
- No-class-balancing outperformed class-balancing for PR-AUC (class balancing trades PR-AUC for recall at the cost of precision)

**Terminology clarification**: "ClsBal" = class-balanced training (`class_weight='balanced'` / `scale_pos_weight`). This addresses label imbalance in the loss function. It is **not** the same as survey weighting, which addresses population representativeness in evaluation.

### 2.2 Stage 6: Tuning

27-configuration grid search: depth x {4,6,8}, learning_rate x {0.03,0.05,0.08}, l2_leaf_reg x {1.0,3.0,5.0}. Iterations: 1200 with early stopping at 80.

**Selected**: depth=6, lr=0.08, l2_leaf_reg=1.0 (PR-AUC 0.6932, +0.0055 over Stage 5 baseline)

### 2.3 Threshold Policy

The default 0.5 threshold is suboptimal for rare-event classification (6.2% positive rate).

| Mode | Threshold | Precision | Recall | F1 |
|------|-----------|-----------|--------|-----|
| Precision-leaning | 0.45 | 0.726 | 0.510 | 0.599 |
| Balanced | 0.25 | 0.585 | 0.683 | 0.630 |
| Recall-leaning | 0.20 | 0.532 | 0.732 | 0.616 |

Threshold recommendations are identical under both unweighted and survey-weighted evaluation, confirming robustness.

### 2.4 Calibration

| Method | Brier Score |
|--------|------------|
| Uncalibrated | 0.0315 |
| Isotonic regression | 0.0317 |
| Platt scaling | 0.0336 |

**Decision**: Calibration not adopted. Brier score is already excellent; neither calibration method improves it. The uncalibrated probabilities are well-calibrated across the full predicted-probability range.

### 2.5 Feature Importance

Top features by CatBoost native importance and SHAP (both agree on the top tier):

| Rank | Feature | CatBoost Imp | SHAP |
|------|---------|-------------|------|
| 1 | family members under 18 | 26.5 | 0.69 |
| 2 | age | 20.9 | 1.06 |
| 3 | veterans benefits | 9.1 | 0.37 |
| 4 | weeks worked in year | 7.0 | 0.83 |
| 5 | sex | 5.1 | 0.41 |
| 6 | education | 4.0 | 0.39 |

No suspicious feature dominance. The model relies on a diverse mix of human-capital, employment, and household signals consistent with economic intuition.

### 2.6 Stability

Year-level subgroup performance (validation, balanced threshold):

| Year | PR-AUC | F1 |
|------|--------|----|
| 94 | 0.6817 | 0.622 |
| 95 | 0.7038 | 0.637 |

Minor temporal variation; no instability concern.

### 2.7 Survey-Weighted Evaluation

All final metrics are reported under both unweighted and survey-weighted evaluation. The same model and thresholds win under both regimes:

| Regime | PR-AUC (Val) | PR-AUC (Test) |
|--------|-------------|---------------|
| Unweighted | 0.6932 | 0.7008 |
| Survey-weighted | 0.6906 | 0.7045 |

Survey-weighted training was intentionally deferred: CPS weights vary 500x (38 to 18,656), and naively passing them as training sample weights would destabilize optimization. The governance requirement is satisfied by survey-weighted evaluation.

## 3. Segmentation Track

### 3.1 Method Selection

**K-Prototypes** was chosen because the dataset is dominated by categorical variables (24 of 31 features). K-Prototypes handles mixed numeric/categorical data natively using Euclidean + Hamming distance, avoiding the information loss of one-hot encoding.

Alternatives considered:
- Gower + hierarchical: conceptually sound but O(n^2) on 200K rows
- K-Means on encoded features: fast but loses categorical structure

### 3.2 Feature Subset

17 features selected for clustering (5 continuous + 12 categorical), focused on life-stage, employment, and household patterns. High-cardinality detail codes (industry/occupation recode, country of birth) excluded to reduce noise.

### 3.3 Subsample Strategy

K-Prototypes was fit on a **random subsample** of 30,000 rows (seed=42) for computational feasibility. Random sampling is appropriate because the dataset is an already-weighted CPS extract with no temporal ordering. Full dataset (199,523 rows) was assigned using the fitted model's predict method.

### 3.4 Segment Count Selection

K-Prototypes was evaluated for k=3 through k=8. In the evaluation outputs, k=3 is stable (smallest cluster 20.4%) while k>=4 consistently produces micro-clusters (0.1%-0.2%).

**Approach**: Request k=4, then absorb clusters smaller than 2% of data into their nearest neighbor by continuous-feature centroid distance. Final result: 3 business-viable segments.

This is preferred over raw k=3 because it makes the outlier-handling explicit and deterministic rather than relying on initialization to fold outliers into a larger cluster.

### 3.5 Governance

- `_target` (income label): **excluded** from clustering input; used only after clustering for profiling
- `_weight` (CPS survey weight): **excluded** from clustering input; used only for population-level segment sizing
- Target enrichment per segment is a profiling metric, not a clustering objective

### 3.6 Limitations

- K-Prototypes is sensitive to initialization (mitigated by Cao init + 5 restarts)
- The segmentation is a useful lens, not ground truth
- The 3-segment solution reflects the dominant life-stage structure; finer segmentation is unstable in this data
- Historical data (1994-1995); real deployment needs current demographics

## 4. What We Intentionally Did Not Do

| Omission | Reason |
|----------|--------|
| Dimensionality reduction (PCA, UMAP) | Not needed — CatBoost handles high-dim categoricals natively; K-Prototypes uses Hamming distance |
| Neural network architectures | Overkill for structured tabular data with strong categorical features |
| Extensive hyperparameter search | Diminishing returns; 27-config grid was sufficient for Stage 6 |
| Survey-weighted training | Methodologically distinct from class balancing; deferred to avoid conflation |
| Stacking / ensemble of multiple models | Single CatBoost is interpretable and performs well; ensemble complexity not justified for a take-home |
| Production deployment pipeline | Out of scope; this is a methodology demonstration |

## 5. Interview-Ready Answers

**Why CatBoost over XGBoost/LightGBM?**
CatBoost has the best native categorical handling among gradient boosting libraries. With 24 categorical features, many with structural sentinels (Not in universe), CatBoost's ordered target encoding avoids the information loss and feature explosion of one-hot encoding.

**Why PR-AUC instead of accuracy?**
The positive class is 6.2%. A "predict everyone as negative" model achieves 93.8% accuracy. PR-AUC measures the model's ability to identify the rare class — the actual business task.

**Why not use the survey weights in training?**
Survey weights address population representativeness, not label imbalance. CPS weights vary 500x. Naively using them as sample weights would let a few high-weight observations dominate gradient updates. Survey-weighted evaluation captures population-representative performance without distorting optimization.

**Why only 3 segments?**
The CPS data has a dominant life-stage structure: children, retirees, and working-age adults. These groups differ on nearly every marketing-relevant dimension. Forcing finer splits produces unstable micro-clusters in the evaluation outputs, not additional actionable groups. The classifier's probability score provides a continuous dimension for sub-targeting within the large working-age segment.

**Why not use the income label in clustering?**
Using the target as a clustering input would create segments that are essentially "high-income" and "low-income" — which the classifier already provides. Marketing segmentation should capture *who people are*, not *what they earn*. Income is then profiled after clustering to enrich the segments with outcome information.
