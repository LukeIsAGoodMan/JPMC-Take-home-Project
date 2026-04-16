# Setup Overview

> Derived from: README.md, SUBMISSION_SUMMARY.md

## Project Objective

Build two complementary tools for retail marketing on weighted CPS census data (199,523 records, 1994-1995):

1. **Income classifier** — ranks individuals by likelihood of earning >$50K
2. **Population segmentation** — groups people by life-stage for differentiated marketing

## Business Framing

This is a **two-layer targeting design**, not just a classifier:
- The classifier answers *who to prioritize* (coarse scoring / routing)
- The segmentation answers *how to approach them* (action design)
- The threshold policy converts score into business decision

Income >$50K is a proxy target. The real business objective is purchasing power, product affinity, and propensity to respond.

## Main Deliverables

| Deliverable | Description |
|------------|-------------|
| Income scoring model | CatBoost classifier with 3 operating thresholds |
| Population segmentation | 3 interpretable life-stage segments |
| Threshold policy | Precision/balanced/recall operating modes |
| Final report | HTML + PDF + markdown documentation package |

## Stage Overview

| Stage | Name | Output |
|-------|------|--------|
| 1-2 | Setup & profiling | Dataset understanding, profiling report |
| 3 | Design | Preprocessing plan, column treatment rules |
| 4 | Preprocessing | Train/val/test splits, segmentation dataset |
| 5 | Baseline | LR vs CatBoost, 8-config comparison |
| 6 | Tuning | 27-config grid, threshold policy, calibration, interpretability |
| 7 | Segmentation | K-Prototypes, 3 final segments |
| 8 | Packaging | README, client report, HTML report, audit layer |

## Environment

- Python 3.11+
- Key packages: pandas, scikit-learn, catboost, kmodes, shap
- Seed: 42 throughout
