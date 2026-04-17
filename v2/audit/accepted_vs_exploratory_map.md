# Accepted vs Exploratory Map

## Status Definitions

| Status | Meaning |
|--------|---------|
| **Accepted** | Part of the final V2 deliverable |
| **Conditionally adopted** | Accepted with documented caveats |
| **Tested, not adopted** | Experiment ran; baseline was better |
| **Design artifact** | Framing/planning doc; not an empirical result |
| **Superseded** | Replaced by a later, more rigorous version |

## Classification by Status

### Accepted
| Artifact | Notes |
|----------|-------|
| CatBoost classifier (V1 params) | Confirmed by benchmark |
| Unweighted training | Confirmed by weighted experiments |
| Score-band analysis | Empirical on validation set |
| Target hierarchy design | Tier 0-3 framework |
| Decision-policy framework | Budget/capacity/V-C logic |
| V1 macro label exact recovery | Verified to match V1 |

### Conditionally Adopted
| Artifact | Condition |
|----------|-----------|
| Layer 2: 3 working-age sub-segments | Exact V1 lineage; 3/4 seed stability; directional boundaries |

### Tested, Not Adopted
| Artifact | Why Not |
|----------|---------|
| Weighted training (normalized) | -0.0036 PR-AUC |
| Weighted training (sqrt) | -0.0045 PR-AUC |
| Weighted training (capped p99) | -0.0056 PR-AUC |
| LightGBM | -0.0093 PR-AUC |
| XGBoost | -0.0103 PR-AUC |

### Design Artifacts (not empirical claims)
| Artifact |
|----------|
| Business objective hierarchy |
| Proxy target upgrade options |
| Campaign playbook V2 |
| Score x segment operating matrix |
| Incremental value of two-layer design |
| Segmentation feature scorecard |

### Superseded (in archive/)
| Artifact | Superseded By |
|----------|--------------|
| `segment2_profiles.md` | `segment2_exact_profiles.md` |
| `segment2_profiles.html` | `segment2_exact_profiles.html` |
| `segment2_second_pass_design.md` | `segment2_exact_second_pass_design.md` |
| `segmentation_v2_results.json` | `segment2_exact_results.json` |
