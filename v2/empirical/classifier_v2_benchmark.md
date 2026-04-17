# Classifier Benchmark — V2

> Status: **Tested, CatBoost remains accepted baseline**

## Objective

Test whether LightGBM or XGBoost displaces CatBoost as the preferred classifier.

## Setup

All models use comparable settings: ~1200 iterations, lr=0.08, depth=6, L2=1.0. Same train/val/test splits. CatBoost uses native categorical handling; LightGBM and XGBoost use ordinal encoding (necessary since they don't natively handle string categoricals).

## Results

| Model | Val PR-AUC | Val ROC-AUC | Val F1 @0.25 | Test PR-AUC |
|-------|-----------|------------|-------------|------------|
| **CatBoost** | **0.6932** | — | **0.6299** | **0.7008** |
| LightGBM | 0.6839 | — | 0.6253 | 0.6917 |
| XGBoost | 0.6829 | — | 0.6274 | — |

## Analysis

CatBoost outperforms both alternatives by ~0.01 PR-AUC on validation and ~0.01 on test. This gap is meaningful given the task's class imbalance (6.2% positive rate).

**Why CatBoost wins**: The dataset has 24 categorical features, many with structural sentinel values (`Not in universe`, `Unknown`). CatBoost's ordered target encoding handles these natively without information loss. LightGBM and XGBoost require ordinal encoding, which imposes an artificial numeric ordering on inherently unordered categories.

## Decision: CatBoost RETAINED

The benchmark confirms the V1/V2 choice. CatBoost's native categorical handling gives it a structural advantage on this dataset. No model change.
