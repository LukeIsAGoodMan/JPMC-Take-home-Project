# Layer 2 Adoption Decision

> Status: **Decision made**

## Questions and Answers

### 1. Was the rerun based on exact V1 Segment 2 labels?

**Yes.** V1 macro labels were exactly recovered via deterministic replay (verified: segment sizes match frozen V1 output to the row). The second-pass was run on exactly the 91,443 rows assigned to V1 Segment 2.

### 2. How many sub-segments emerged?

**3 sub-segments** (from k=4 + micro-cluster absorption):
- Established Mid-Career Earners (38%, 20.7% >50K)
- Lower-Income Service Workers (11%, 2.4% >50K)
- Younger Mainstream Workers (51%, 8.6% >50K)

### 3. Are they stable?

**Partially.** 3 of 4 seeds produce 3 sub-segments; 1 produces 2. The ~10K low-income service-worker group is consistent across all seeds. The split between the two larger groups is seed-dependent — their relative sizes vary by 15-20 percentage points across seeds.

### 4. Do they create incremental value?

**Yes, meaningfully:**
- The V1 macro working-age segment (91K rows) treated all working-age adults as one group with a 12.5% >50K rate
- The sub-segments reveal a 9x difference in income rate within that group (20.7% vs 2.4%)
- This directly enables differentiated targeting: premium outreach for Sub-0, accessible products for Sub-1, growth offers for Sub-2

This is more useful than:
- V1 macro alone (which gives no within-working-age differentiation)
- The classifier score alone (which ranks but doesn't explain *why* — the sub-segments provide the "who are they" layer)

### 5. Adoption Decision

**Classification: CONDITIONALLY ADOPTED as Layer 2.**

**Rationale**:
- Exact V1 lineage: confirmed
- Business utility: high — 3 distinct sub-segments with clear marketing implications
- Stability: partial — the 3-segment structure appears in 3 of 4 seeds, but cluster boundaries shift

**Conditions**:
- The sub-segment labels should be treated as **directional guides**, not precise boundaries
- The service-worker group (~11%) is the most stable finding; the split between established and younger workers is softer
- For production use, periodic re-validation would be required
- The classifier score remains the primary individual-level targeting dimension; sub-segments provide group-level action design

**What "conditionally adopted" means**:
- Acceptable for inclusion in V2 deliverables and business recommendations
- Must be presented with the stability caveat
- Not treated as a permanent, immutable population structure
