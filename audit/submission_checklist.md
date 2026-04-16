# Submission Checklist

> Final QA checklist before project submission.

## Required Deliverables

| Item | File | Status |
|------|------|--------|
| Final report (HTML) | FINAL_REPORT.html | Done |
| Final report (PDF) | FINAL_REPORT.pdf | Done |
| Client report | CLIENT_REPORT.md | Done |
| README | README.md | Done |
| Technical appendix | TECHNICAL_APPENDIX.md | Done |
| Submission summary | SUBMISSION_SUMMARY.md | Done |
| Audit layer | audit/ (10 files) | Done |

## Classification Artifacts

| Item | Location | Status |
|------|----------|--------|
| Preprocessing code | pipeline/preprocess.py | Done |
| Baseline code | pipeline/classify_baseline.py | Done |
| Tuning code | pipeline/classify_stage6.py | Done |
| Baseline metrics | pipeline/outputs/stage5/BASELINE_METRICS.md | Done |
| Final metrics | pipeline/outputs/stage6/STAGE6_FINAL_METRICS.md | Done |
| Threshold policy | pipeline/outputs/stage6/THRESHOLD_POLICY_REPORT.md | Done |
| Calibration report | pipeline/outputs/stage6/CALIBRATION_REPORT.md | Done |
| Feature importance | pipeline/outputs/stage6/FEATURE_INTERPRETATION_REPORT.md | Done |

## Segmentation Artifacts

| Item | Location | Status |
|------|----------|--------|
| Segmentation code | pipeline/segment_stage7.py | Done |
| Method selection | pipeline/outputs/stage7/SEGMENTATION_METHOD_SELECTION.md | Done |
| Segment profiles | pipeline/outputs/stage7/SEGMENT_PROFILES.md | Done |
| Action playbook | pipeline/outputs/stage7/SEGMENTATION_ACTION_PLAYBOOK.md | Done |
| Segment profiles (HTML) | audit/segment_profiles.html | Done |

## Consistency Checks

| Check | Expected | Status |
|-------|----------|--------|
| Classifier config matches across docs | depth=6, lr=0.08, l2=1.0 | Verified |
| Threshold values consistent | 0.45 / 0.25 / 0.20 | Verified |
| Calibration = not adopted | All docs | Verified |
| Segmentation = 3 final segments | All docs | Verified |
| k=4 is intermediate, not final count | All docs | Verified |
| Random subsample (not stratified) | All docs | Verified |
| Target excluded from clustering | All docs | Verified |
| Weight excluded from features | All docs | Verified |
| PR-AUC test = 0.7008 | All docs | Verified |
| No "stratified subsample" claims | All docs | Verified |
| No "every k from 3-8" over-claims | All docs | Verified |

## Packaging Checks

| Check | Status |
|-------|--------|
| No external cloud storage links | Verified |
| All scripts runnable from clean environment | Verified |
| Seed = 42 throughout | Verified |
| No hardcoded absolute paths in scripts | Verified |
| References section included | Verified |
| HTML report opens locally without internet | Verified |
| PDF renders correctly | Verified |

## Final Sanity

- [ ] Skim FINAL_REPORT.html end-to-end in browser
- [ ] Verify PDF pagination looks reasonable
- [ ] Run `python preprocess.py` from clean state to confirm reproducibility
- [ ] Confirm all markdown renders in GitHub preview
