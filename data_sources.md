# Data Sources

## Project

Austria vs EU27 Macro Observation Card

## Purpose

This file documents the public source base for the current source-bounded observation card.

The current artifact uses official Eurostat observations to compare Austria with EU27_2020 across selected latest official macro indicators.

## Source registry

| Source | Institution | Main use | Geography | Source role | Limitation |
|---|---|---|---|---|---|
| Eurostat | European Union statistical office | Official observations for GDP growth, HICP inflation, HICP energy, unemployment, government debt, and government balance | Austria and EU27_2020 | Current artifact source | Requires careful period, frequency, unit, and definition checks |

## Source use by project artifact

| Artifact | Source needs |
|---|---|
| Austria vs EU27 Macro Observation Card | Eurostat only |
| Official observation table | Eurostat only |
| Latest-observation matrix | Derived from `data/official_macro_indicators.csv` |

## Source documentation fields

Each source used in the project should be recorded with:

- source name,
- source URL,
- institution,
- topic,
- geography,
- source period,
- date accessed,
- project artifact where used,
- value used,
- limitation.

## Source quality rule

Prefer institutional sources for public claims.

Do not add media sources to the current artifact.

Do not add projection sources to official observation rows.

## Projection handling

Projection values are outside the current artifact.

If a later phase adds projection sources, those values must be labelled as projections from the publishing institution and kept separate from official observation rows.

Avoid wording such as:

- Inflation will be...
- Growth will definitely...
- This proves that...
- This proves an adverse outcome...

## Geography and denominator checks

Before using any value, check:

- geography: Austria or EU27_2020,
- time period: month, quarter, or calendar year,
- unit: percent, percentage points, index, level,
- denominator: GDP, labour force, consumer basket or other base,
- source date,
- whether the value is an official observation from an approved Eurostat path.

## Known source risks

Potential source risks include:

- different publication dates,
- mismatched geographies,
- mixing EU and euro area values,
- mixing HICP inflation and national CPI inflation,
- treating latest observations as synchronized real-time conditions,
- reading source-bounded observations as complete economic truth.

## Safe source interpretation

A source supports an observation only within its own scope.

Eurostat supports harmonised historical comparison only within the selected dataset definitions, geographies, periods, frequencies, and units.

## Strongest safe source claim

The current project is source-feasible as a bounded Austria vs EU27_2020 macro observation card because the included indicators are covered by official Eurostat datasets.

The source base does not support a validated forecasting model, objective country-risk ranking, investment recommendation, policy recommendation, crisis diagnosis, stress score, or synchronized real-time condition claim.
