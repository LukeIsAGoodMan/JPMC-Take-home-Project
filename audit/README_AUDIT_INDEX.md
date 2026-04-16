# Audit Index

## Why This Folder Exists

The original project blueprint specifies a set of stage-aligned documentation files by name. The main submission uses a different (cleaner) document structure optimized for readability. This `audit/` folder provides the blueprint-aligned files as an additive traceability layer.

**This folder does NOT replace the main submission documents** (`README.md`, `CLIENT_REPORT.md`, `TECHNICAL_APPENDIX.md`, `FINAL_REPORT.html`). It maps to them.

## File Index

| Blueprint File | Purpose | Derived From |
|---------------|---------|-------------|
| `setup_overview.md` | Project kickoff / scope / framing | README.md, SUBMISSION_SUMMARY.md |
| `eda_summary.md` | Exploratory data analysis summary | summary_report_full.md, PREPROCESSING_AUDIT.md |
| `preprocessing_plan.md` | Preprocessing governance decisions | PREPROCESSING_AUDIT.md, column_treatment.md |
| `pipeline_design.md` | End-to-end pipeline architecture | README.md, SUBMISSION_SUMMARY.md |
| `classification_baseline.md` | Stage 5 baseline comparison | BASELINE_METRICS.md, CLASSIFIER_BASELINE_REPORT.md |
| `classification_model_selection.md` | Final classifier selection | MODEL_SELECTION_REPORT.md, STAGE6_FINAL_METRICS.md, THRESHOLD_POLICY_REPORT.md |
| `segmentation_design.md` | Segmentation rationale and design | SEGMENTATION_METHOD_SELECTION.md, SEGMENTATION_REPORT.md |
| `segment_profiles.html` | Visual segment profiles | SEGMENT_PROFILES.md, SEGMENTATION_ACTION_PLAYBOOK.md |
| `client_report_draft.md` | Blueprint-aligned client report | CLIENT_REPORT.md |
| `submission_checklist.md` | Final QA checklist | All artifacts |
