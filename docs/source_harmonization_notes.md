# Source Harmonization Notes

## Scope

This note records Phase 2 official source-ID validation and source-boundary decisions only.

It does not introduce analytical findings, forecasts, rankings, investment claims, policy claims, crisis labels, synthetic risk scores, or validated monitoring-system claims.

## Validated Eurostat source paths

The selected MVP source paths use official Eurostat observation datasets:

- Real GDP growth: `nama_10_gdp`, `na_item=B1GQ`, `unit=CLV_PCH_PRE`. Source label validated as annual GDP and main components, with gross domestic product at market prices measured as chain linked volumes, percentage change on previous period.
- HICP inflation: `prc_hicp_aind`, `coicop=CP00`, `unit=RCH_A_AVG`. Source label validated as HICP annual data, with all-items HICP measured as annual average rate of change.
- Energy inflation: `prc_hicp_aind`, `coicop=NRG`, `unit=RCH_A_AVG`. Source label validated as the HICP energy aggregate measured as annual average rate of change.
- Unemployment rate: `une_rt_m`, `age=TOTAL`, `sex=T`, `unit=PC_ACT`, `s_adj=SA`. Source label validated as monthly unemployment by sex and age, total age aggregate, total sex, percentage of the labour force, seasonally adjusted.
- General government gross debt percent of GDP: `gov_10dd_edpt1`, `sector=S13`, `na_item=GD`, `unit=PC_GDP`. Source label validated as government consolidated gross debt for general government, percentage of GDP.
- General government deficit/surplus percent of GDP: `gov_10dd_edpt1`, `sector=S13`, `na_item=B9`, `unit=PC_GDP`. Source label validated as net lending (+)/net borrowing (-) for general government, percentage of GDP.

## Deferred or rejected candidates

- `namq_10_gdp` is validated as an official quarterly GDP dataset, but deferred because Phase 2 selects the annual GDP path. Quarterly GDP should only be added after an explicit quarterly architecture decision.
- `prc_hicp_manr` is validated as an official monthly HICP annual-rate dataset, but deferred because Phase 2 selects the annual HICP path. Re-check monthly replacement or continuity before using it.
- `ei_lmhr_m`, `une_rt_a`, and `tipsun20` were checked as unemployment alternatives. They are deferred because `une_rt_m` is the selected monthly unemployment path with standard age and sex dimensions.
- `tec00127` is validated as a general government deficit/surplus view, but deferred in favor of `gov_10dd_edpt1` so the selected debt and balance indicators share the underlying government finance source dataset.
- `CP045` in HICP is electricity, gas and other fuels. It is not selected as the primary energy indicator because Eurostat exposes the broader `NRG` HICP energy aggregate.

## Indicator definition choices

The Phase 2 architecture separates source metadata from observation rows:

- `data/source_registry.csv` records source IDs, official dataset codes, source indicator definitions, units, frequency, and validation status.
- `data/official_macro_indicators_schema.csv` defines the observation-row shape for later data loading.
- The source-harmonization schema step did not load numeric observations; the subsequent bounded retrieval prototype writes latest available official Eurostat observations to `data/official_macro_indicators.csv`.
- Projection sources must not be mixed into official observation rows.
- Each future observation row should preserve source ID, dataset code, indicator code, geography, period, frequency, unit, retrieval timestamp, and revision status where available.

## Retrieval prototype note

The first bounded Eurostat retrieval prototype writes `data/official_macro_indicators.csv` from official Eurostat API responses only.

Retrieval logic:

- filter each request to one approved `source_id`, dataset path, indicator definition, and geography,
- select the latest returned time period with a non-blank numeric value,
- preserve source period labels, units, frequency, source release timestamp, and retrieval timestamp,
- include rows only when the retrieved dimensions match the approved MVP definition.

Geography handling:

- Austria uses Eurostat `AT`.
- The EU aggregate uses Eurostat `EU27_2020` where it is returned cleanly by the approved datasets.

Rows omitted:

- Monthly unemployment rows use `une_rt_m` with `age=TOTAL`, `sex=T`, `unit=PC_ACT`, and `s_adj=SA` after supervisor approval revised the monthly definition from the unavailable `Y15-74` monthly age code.
- The unemployment path remains the only approved monthly indicator, so frequency mismatch should be preserved in downstream tables and notes.

## Claim boundary

Allowed uses of these validated paths:

- official-source observation tables,
- source-bounded comparison tables,
- country/source availability matrices,
- indicator metadata,
- latest available observation dates,
- unit, frequency, source-ID, and recency notes,
- data-gap maps with bounded analytical meaning.

Forbidden uses without a separate approved method:

- crisis prediction,
- recession forecast,
- investment signal,
- policy recommendation,
- objective country ranking,
- validated early-warning model,
- synthetic risk score.

## Strongest safe Phase 2 statement

The project may show how selected official indicators place Austria and Europe across several macro-stress channels at the latest available observation point, while preserving source, frequency, unit, coverage, and recency limits.
