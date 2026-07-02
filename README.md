# Europe Macro Stress Monitor 2026

A source-bounded official observation prototype for selected European macro-stress channels, with Austria as a focused country case and EU27_2020 as the comparison aggregate.

## Current Status

This repository currently contains a source-bounded official observation prototype.

Current public scope:

- validated Eurostat source paths for selected macro indicators,
- a bounded 12-row official observation table for Austria and EU27_2020,
- a 6-row latest-observation matrix across selected macro-stress channels,
- methodology and claim-boundary notes for reading the data cautiously.

Release status: no formal release yet.

## What Is Included

The current official data artifacts are:

- `data/source_registry.csv`: validated Eurostat source paths and deferred source candidates,
- `data/official_macro_indicators.csv`: latest available official observations for Austria and EU27_2020,
- `data/latest_official_macro_stress_matrix.csv`: source-bounded latest-observation matrix across selected macro-stress channels.

The selected channels are:

- real GDP growth,
- HICP inflation,
- HICP energy inflation,
- unemployment rate,
- general government gross debt percent of GDP,
- general government deficit/surplus percent of GDP.

## How To Read The Data

Values are latest available official observations from the recorded Eurostat source paths.

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

## Boundaries / What This Is Not

This project is:

- a source-bounded official observation prototype,
- a structured view of selected official Eurostat observations,
- a cautious way to compare Austria and EU27_2020 across selected channels.

This project is not a forecast model.

It is also:

- not an investment signal,
- not a policy recommendation tool,
- not an objective country ranking,
- not a validated early-warning model.

The data should not be read as crisis prediction, recession prediction, market advice, policy advice or complete macroeconomic coverage.

## Reproducibility Note

The observation table records the source ID, dataset code, indicator code, geography, period, unit, retrieval timestamp and source release timestamp for each included row.

The latest-observation matrix is derived only from `data/official_macro_indicators.csv`. It does not fetch new data or change source observation values.

## Methodology

See `methodology.md` and `docs/source_harmonization_notes.md` for source-boundary and claim-boundary details.
