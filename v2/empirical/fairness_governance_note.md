# Fairness & Sensitive Feature Governance Note

> Status: **Completed governance artifact**

## Demographic Features Used in the Model

The classifier and segmentation use several demographic features that are sensitive in a fairness context:

| Feature | Used In | Sensitivity |
|---------|---------|-------------|
| `sex` | Classifier + segmentation | Protected class in most jurisdictions |
| `race` | Classifier only | Protected class |
| `hispanic origin` | Classifier only | Protected class / ethnicity proxy |
| `age` | Classifier + segmentation | Protected in employment; proxy for life-stage |
| `citizenship` | Classifier + segmentation | Immigration status proxy |
| `marital stat` | Classifier + segmentation | Proxy for household economics |
| `country of birth self/father/mother` | Classifier only | National origin proxy |

## Why These Features Are Included

These features are included because the project objective is **population profiling for marketing segmentation**, not individual-level credit, employment, or housing decisions. In a marketing-analytics context:

1. Demographic features are standard segmentation dimensions (age, life-stage, household type)
2. The model is an analytical tool, not an automated decision system
3. No individual adverse action is taken based on model output alone
4. The take-home project explicitly asks for demographic-based income prediction

## Governance Caveats

1. **This is a take-home analytical exercise, not a production deployment.** No real individuals are affected by the model's outputs.

2. **If deployed in production**, demographic features would require review under applicable regulations (ECOA, Fair Housing Act, state-level consumer protection laws) depending on the use case.

3. **Marketing use cases** generally have more latitude than credit/employment decisions, but responsible use still requires:
   - Avoiding discriminatory targeting that excludes protected groups from beneficial offers
   - Ensuring that high-income targeting doesn't systematically deprioritize protected classes
   - Monitoring for disparate impact in campaign outcomes

4. **The segmentation's life-stage structure** (seniors, youth, working-age) is driven by age and employment status. This is standard marketing practice but should be reviewed if the segments are used for anything beyond marketing.

5. **Survey weights** partially correct for sampling bias but do not address potential bias in the underlying income-to-demographics relationship.

## What This Project Does NOT Do

- Does not conduct a formal disparate impact analysis
- Does not compute equalized odds, demographic parity, or other fairness metrics
- Does not build a fairness-constrained model
- Does not assess whether the income threshold ($50K in 1994) has different implications across demographic groups

These would be appropriate next steps if the model were to be deployed in a real business context.

## Recommendation

For a take-home project: the current approach is acceptable with this governance note documenting the sensitivity.

For production: a fairness impact assessment should be conducted before deployment, with the scope determined by the specific use case (marketing vs credit vs employment).
