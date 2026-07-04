# Methodology

## Project

Austria vs EU27 Macro Observation Card

## Purpose

This project uses a source-bounded macro observation approach. It compares selected latest official Eurostat observations for Austria and EU27_2020 while preserving source periods, units, frequencies, and boundary notes.

The current artifact is a bounded observation snapshot. It is not a forecast, objective risk score, country ranking, policy recommendation, investment recommendation, crisis diagnosis, or synchronized real-time macro condition view.

## Current artifact

The current public artifact contains:

- validated Eurostat source paths for selected macro indicators,
- a bounded official observation table for Austria and EU27_2020,
- a latest-observation matrix across selected macro observation channels,
- notes that preserve source, frequency, unit, period, and claim boundaries.

The selected channels are:

1. Real GDP growth
2. HICP inflation
3. HICP energy inflation
4. Unemployment rate
5. General government gross debt percent of GDP
6. General government deficit/surplus percent of GDP

## Core method

The method has four steps:

1. Validate each official Eurostat source path and indicator definition.
2. Retrieve only the latest available official observations for Austria and EU27_2020 from the approved source paths.
3. Preserve source values, periods, units, frequencies, dataset codes, indicator codes, source IDs, and boundary notes.
4. Present the results as a source-bounded observation matrix, not as a score or ranking.

## Possible future artifacts, not part of the current artifact

Earlier scaffold concepts such as broader map, watchlist, energy-transmission, and fiscal-pressure artifacts are not current project outputs. They would require separate Data Proof, source-boundary review, and public wording review before being presented as current artifacts.

## Interpretation rules

Each observation should answer four questions:

1. What does the source report?
2. What geography, period, frequency, and unit does it use?
3. Is Austria above, below, or close to EU27_2020 for this included indicator?
4. What must not be claimed?

## Claim boundary

The project may describe selected official observations and cautious Austria vs EU27_2020 comparisons.

The project must not claim:

- recession certainty,
- interest-rate forecasts,
- asset-price forecasts,
- investment recommendations,
- policy recommendations,
- objective country-risk rankings,
- validated early-warning capability,
- synchronized real-time macro conditions,
- complete macroeconomic coverage.

## Source rules

The current artifact uses official Eurostat observations only. Each included row should preserve:

- source ID,
- official dataset code,
- indicator code,
- geography,
- source period,
- frequency,
- unit,
- retrieved value,
- retrieval timestamp when available,
- source release timestamp when available,
- interpretation boundary note.

## Official source harmonization boundary

Official observation rows should use validated source IDs and indicator definitions before any public analytical wording is expanded.

The selected official Eurostat observation paths are:

- annual real GDP growth: `nama_10_gdp`, `B1GQ`, chain linked volumes, percentage change on previous period,
- annual HICP inflation: `prc_hicp_aind`, `CP00`, annual average rate of change,
- annual HICP energy inflation: `prc_hicp_aind`, `NRG`, annual average rate of change,
- monthly unemployment rate: `une_rt_m`, total age aggregate, total sex, percentage of the labour force, seasonally adjusted,
- general government gross debt: `gov_10dd_edpt1`, `GD`, general government, percentage of GDP,
- general government deficit/surplus: `gov_10dd_edpt1`, `B9`, net lending (+)/net borrowing (-), general government, percentage of GDP.

These paths support official-source observations and source-bounded comparison tables only. They do not support crisis prediction, recession forecasts, investment signals, policy recommendations, objective country rankings, validated early-warning claims, synthetic risk scores, or synchronized real-time condition claims.

## Update logic

The observation table may be refreshed when Eurostat releases updated values for the approved datasets. A refresh should preserve the same source IDs and definitions unless a separate source-harmonization review approves a change.

The current method does not require new sources, broader country coverage, or new indicator families.

## Limits

This methodology does not produce quantitative forecasts.

It does not estimate causal effects unless a source directly supports the causal claim.

It does not aggregate indicators into a weighted score.

It does not rank Austria against other countries by macroeconomic risk.

It does not claim that observed differences establish macro stress, recession, crisis, market losses or policy changes.

## Strongest safe methodological claim

The current artifact supports a cautious Austria-vs-EU27_2020 observation snapshot across selected official macro indicators. It can show visible indicator differences, but it does not establish macro stress, predict outcomes, rank risk, or diagnose economic conditions.

## Possible future v2, not part of the current artifact

A possible future v2 could test an EU27 Macro Deviation Extremes Card, identifying the highest positive and highest negative deviation from EU27_2020 by channel while showing Austria as a marked case. This would require a separate Data Proof for EU27 coverage, period/frequency compatibility, and safe non-risk-ranking wording.
