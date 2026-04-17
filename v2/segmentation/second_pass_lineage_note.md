# Second-Pass Segmentation — Lineage Note

## Population Definition Used

The second-pass clustering was run on a **rules-based approximation** of the V1 working-age macro segment:

```
working_age = (age >= 18) AND (education != "Children") AND NOT (age >= 55 AND weeks_worked < 10)
```

This produced 116,329 rows (58.3% of population).

## How This Differs From V1 Macro Labels

V1's macro segments were produced by K-Prototypes clustering on the full population. The V1 Segment 2 (working-age) contained 91,443 rows (45.8%). The rules-based approximation captures a **larger and overlapping but not identical** population:

| Definition | Rows | % of Total |
|-----------|-----:|----------:|
| V1 K-Prototypes Segment 2 | 91,443 | 45.8% |
| Rules-based approximation | 116,329 | 58.3% |
| Difference | ~24,886 | ~12.5% |

The rules-based set is ~27% larger because V1 K-Prototypes assigned some working-age individuals to the senior cluster (e.g., non-working 50-54 year olds) or the youth cluster (e.g., 18-year-old students). The approximation uses simpler age/education/employment rules that don't perfectly replicate the multivariate K-Prototypes assignment.

## Are V1 Macro Labels Recoverable?

**Not directly from saved artifacts.** V1's `segment_stage7.py` produces labels during execution but does not save per-row segment assignments to disk. The saved `stage7_results.json` contains profiles and names but not row-level labels.

To recover exact V1 labels, one would need to:
1. Re-run `segment_stage7.py` (which is deterministic with seed=42)
2. Save the `labels_full` array to a file
3. Use those labels to filter the working-age population

This is feasible but was not done in the current V2 pass.

## Consequence for Second-Pass Status

Because the second-pass clustering operated on an approximate population that does not exactly match frozen V1 Segment 2, the result **cannot be classified as a formally adopted Layer 2 segmentation**. It is an **exploratory empirical result** that is informative for V2 design but has a known lineage gap.

## What Would Be Required for Formal Adoption

1. Re-run V1 `segment_stage7.py` to extract per-row macro labels
2. Filter to exactly the rows assigned to V1 Segment 2
3. Re-run second-pass K-Prototypes on that exact population
4. Evaluate whether the result is operationally useful (more than 2 sub-segments, stable)
5. If yes, promote to adopted Layer 2

This is a clean, bounded task but was deferred in favor of completing the broader V2 design pass.
