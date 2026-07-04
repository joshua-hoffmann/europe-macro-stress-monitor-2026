# Austria vs EU27 Macro Observation Card

This repository contains a source-bounded observation card comparing Austria with EU27_2020 across selected latest official Eurostat macro indicators. It is designed for cautious comparison of official observations, not for forecasting, scoring, ranking, policy advice, investment advice, or real-time condition monitoring.

## Current Status

This repository currently contains a source-bounded macro observation prototype.

Current public scope:

- validated Eurostat source paths for selected macro indicators,
- a bounded 12-row official observation table for Austria and EU27_2020,
- a 6-row latest-observation matrix across selected macro observation channels,
- methodology and claim-boundary notes for reading the data cautiously.

Release status: public prototype release exists; this refresh only updates public wording and does not create a new release or tag.

## What Is Included

The current official data artifacts are:

- `data/source_registry.csv`: validated Eurostat source paths and deferred source candidates,
- `data/official_macro_indicators.csv`: latest available official observations for Austria and EU27_2020,
- `data/latest_official_macro_stress_matrix.csv`: source-bounded latest-observation matrix across selected macro observation channels.

Note: `data/latest_official_macro_stress_matrix.csv` preserves an earlier working filename. The public interpretation is a source-bounded observation matrix, not a stress score or early-warning system.

The selected channels are:

- real GDP growth,
- HICP inflation,
- HICP energy inflation,
- unemployment rate,
- general government gross debt percent of GDP,
- general government deficit/surplus percent of GDP.

## How To Read The Data

Values are latest available official observations from the recorded Eurostat source paths.

The card compares latest available official observations. Periods and frequencies may differ by indicator. The values should be read as source-bounded observations, not synchronized real-time conditions.

The matrix preserves:

- source values as reported,
- source periods,
- units,
- frequency,
- source IDs,
- dataset codes,
- indicator codes,
- comparability groups,
- boundary notes.

The matrix is designed for source-bounded comparison. It does not compute differences, create country rankings or convert observations into summary signals.

Austria can be shown as a source-bounded latest-observation case against EU27_2020 across selected official macro indicators. The current artifact supports cautious deviation-style reading, but it does not support a stress score, risk ranking, forecast, or diagnosis.

## Boundaries / What This Is Not

This project is:

- a source-bounded official observation prototype,
- a structured view of selected official Eurostat observations,
- a cautious way to compare Austria and EU27_2020 across selected channels.

This project is not:

- a forecast,
- a stress score,
- an investment signal,
- a policy recommendation tool,
- a crisis diagnosis,
- a real-time monitoring system,
- an objective country-risk ranking,
- a validated early-warning model,
- complete macroeconomic coverage.

The data should not be read as synchronized real-time conditions, market advice, policy advice, or complete economic truth.

## Reproducibility Note

The observation table records the source ID, dataset code, indicator code, geography, period, unit, retrieval timestamp and source release timestamp for each included row.

The latest-observation matrix is derived only from `data/official_macro_indicators.csv`. It does not fetch new data or change source observation values.

## Methodology

See `methodology.md` and `docs/source_harmonization_notes.md` for source-boundary and claim-boundary details.
