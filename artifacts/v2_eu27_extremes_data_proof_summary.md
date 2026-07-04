# V2 EU27 Extremes Data Proof Summary

## Scope

This proof tests whether selected official Eurostat channels can support an EU27 Macro Deviation Extremes Card showing where Austria sits relative to EU27_2020 and observed EU27 country extremes.

No v1 data files, public docs, release files, tags, or repository settings are changed by this script.

## Output

- CSV: `artifacts/v2_eu27_extremes_data_proof.csv`
- Retrieved at: `2026-07-04T15:34:08.901838+00:00`

## Channel Results

| Channel | EU27_2020 period | Coverage | Highest positive deviation | Highest negative deviation | Austria deviation | Decision |
|---|---:|---:|---|---|---:|---|
| Real GDP growth | 2025 | 27/27 | Ireland (+6.500) | Germany (-1.300) | -0.700 | PASS |
| HICP inflation | 2025 | 27/27 | Romania (+4.300) | Cyprus (-1.700) | +1.100 | PASS |
| HICP energy inflation | 2025 | 27/27 | Austria (+8.200) | France (-4.800) | +8.200 | PASS |
| Unemployment rate | 2026-05 | 27/27 | Finland (+4.900) | Bulgaria (-3.000) | -0.100 | PASS |
| Government gross debt | 2025 | 27/27 | Greece (+64.400) | Estonia (-57.600) | -0.200 | PASS |
| Government balance | 2025 | 27/27 | Cyprus (+6.500) | Romania (-4.800) | -1.100 | PASS |

## Bounded Insight Check

The proof is useful if at least four channels provide EU27_2020, Austria, at least 20 compatible EU27 country observations, and visible positive/negative deviations without aggregating across channels.

Current proof decision: **PROCEED TO INSIGHT PROOF**.

## Boundary

The output identifies highest positive and highest negative deviations from EU27_2020 within each source-bounded channel. It does not classify countries, aggregate channels, or create advisory, predictive, diagnostic, market-use, or policy-use outputs.
