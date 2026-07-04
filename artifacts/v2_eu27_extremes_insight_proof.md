# V2 EU27 Extremes Insight Proof

## Task

Test whether the v2 extremes structure produces a viewer-friendly draft artifact showing where Austria sits relative to EU27_2020 and observed EU27 country extremes by channel.

## Files used

- `artifacts/v2_eu27_extremes_data_proof.csv`
- `artifacts/v2_eu27_extremes_data_proof_summary.md`

## Files created

- `analysis/v2_eu27_extremes_insight_proof.py`
- `artifacts/v2_eu27_extremes_card_draft.png`
- `artifacts/v2_eu27_extremes_insight_proof.md`

## Visual artifact

The draft card uses one horizontal range per channel:

- left endpoint: highest negative deviation from EU27_2020,
- center reference: EU27_2020 = 0 deviation,
- black diamond: Austria deviation from EU27_2020,
- right endpoint: highest positive deviation from EU27_2020,
- row note: observation period, frequency, and percentage-point deviation unit.

## Insight proof checks

- Understandable within 60 seconds: yes. The card uses the same visual grammar for all six channels and labels Austria directly on each range.
- More than a low-value table: yes. It shows Austria's position within the observed country-deviation range rather than listing only endpoint values.
- Austria relative to EU27 country extremes is visible: yes, especially for HICP energy inflation where Austria equals the highest positive deviation.
- Classification implication avoided: yes. The draft uses source-bounded deviation wording and does not aggregate channels.
- Period/frequency boundary visible: yes. Annual channels are labelled 2025 Annual, and unemployment is labelled 2026-05 Monthly.

## Strongest bounded insight

Within the selected official Eurostat observations, Austria is the highest positive deviation case for HICP energy inflation (+8.200 p.p. vs EU27_2020), while Austria sits close to EU27_2020 for unemployment (-0.100 p.p.) and government gross debt (-0.200 p.p.). This creates a clear Austria-relative-to-extremes story without aggregating channels or classifying country risk.

## Visual and claim risks

- Per-channel ranges use separate scales, so the draft should not be read as comparing magnitudes across rows by line length.
- Annual and monthly channels are placed in the same card, so the period/frequency labels must remain visible.
- The draft should keep neutral endpoint language: highest positive deviation and highest negative deviation.
- The draft should not be converted into a composite index or country classification.

## Decision

PROCEED TO HERO ARTIFACT

## Reason

All 6 channels passed Data Proof, and the draft card communicates a non-generic Austria-relative-to-extremes pattern without using aggregation or normative labels.

## Boundary

Source-bounded latest official observations only. No predictive, scoring, ranking, market-use, policy-use, or diagnostic claims.
