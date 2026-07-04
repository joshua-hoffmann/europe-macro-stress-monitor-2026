from __future__ import annotations

import csv
import json
import math
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = PROJECT_ROOT / "data" / "source_registry.csv"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
OUTPUT_CSV = ARTIFACTS_DIR / "v2_eu27_extremes_data_proof.csv"
SUMMARY_MD = ARTIFACTS_DIR / "v2_eu27_extremes_data_proof_summary.md"

EU27_COUNTRIES = [
    "BE",
    "BG",
    "CZ",
    "DK",
    "DE",
    "EE",
    "IE",
    "EL",
    "ES",
    "FR",
    "HR",
    "IT",
    "CY",
    "LV",
    "LT",
    "LU",
    "HU",
    "MT",
    "NL",
    "AT",
    "PL",
    "PT",
    "RO",
    "SI",
    "SK",
    "FI",
    "SE",
]
BENCHMARK_GEO = "EU27_2020"
ALL_GEOS = [BENCHMARK_GEO] + EU27_COUNTRIES


@dataclass(frozen=True)
class ChannelSpec:
    channel: str
    source_id: str
    dataset_code: str
    query: dict[str, str]
    frequency: str
    boundary_note: str


SPECS = [
    ChannelSpec(
        channel="Real GDP growth",
        source_id="eurostat_gdp_annual_growth_real",
        dataset_code="nama_10_gdp",
        query={"freq": "A", "na_item": "B1GQ", "unit": "CLV_PCH_PRE"},
        frequency="Annual",
        boundary_note="Latest official annual observation under the selected Eurostat path; deviations are percentage-point differences from EU27_2020.",
    ),
    ChannelSpec(
        channel="HICP inflation",
        source_id="eurostat_hicp_annual_all_items",
        dataset_code="prc_hicp_aind",
        query={"freq": "A", "coicop": "CP00", "unit": "RCH_A_AVG"},
        frequency="Annual",
        boundary_note="Latest official annual-average HICP observation; deviations are percentage-point differences from EU27_2020.",
    ),
    ChannelSpec(
        channel="HICP energy inflation",
        source_id="eurostat_hicp_annual_energy",
        dataset_code="prc_hicp_aind",
        query={"freq": "A", "coicop": "NRG", "unit": "RCH_A_AVG"},
        frequency="Annual",
        boundary_note="Latest official annual-average HICP energy component observation; not a broad energy-pressure proxy.",
    ),
    ChannelSpec(
        channel="Unemployment rate",
        source_id="eurostat_unemployment_monthly_rate",
        dataset_code="une_rt_m",
        query={"freq": "M", "age": "TOTAL", "sex": "T", "unit": "PC_ACT", "s_adj": "SA"},
        frequency="Monthly",
        boundary_note="Latest official monthly unemployment observation; monthly frequency differs from annual channels.",
    ),
    ChannelSpec(
        channel="Government gross debt",
        source_id="eurostat_government_debt_gross",
        dataset_code="gov_10dd_edpt1",
        query={"freq": "A", "sector": "S13", "na_item": "GD", "unit": "PC_GDP"},
        frequency="Annual",
        boundary_note="Latest official general-government gross debt observation; not a debt-sustainability assessment.",
    ),
    ChannelSpec(
        channel="Government balance",
        source_id="eurostat_government_balance_b9",
        dataset_code="gov_10dd_edpt1",
        query={"freq": "A", "sector": "S13", "na_item": "B9", "unit": "PC_GDP"},
        frequency="Annual",
        boundary_note="Latest official net lending/net borrowing observation; sign is preserved.",
    ),
]


def read_registry() -> dict[str, dict[str, str]]:
    with REGISTRY_PATH.open(newline="", encoding="utf-8-sig") as f:
        return {row["source_id"]: row for row in csv.DictReader(f)}


def eurostat_url(dataset: str, query: dict[str, str]) -> str:
    params: dict[str, str] = {"lang": "en", "format": "JSON"}
    params.update(query)
    return f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset}?{urlencode(params)}"


def fetch_json(url: str) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "source-bounded-v2-data-proof/1.0"})
    with urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def dimension_label(response: dict[str, Any], dimension: str, code: str) -> str:
    try:
        return response["dimension"][dimension]["category"]["label"].get(code, code)
    except KeyError:
        return code


def latest_observation(dataset: str, base_query: dict[str, str], geo: str) -> dict[str, Any]:
    query = dict(base_query)
    query["geo"] = geo
    url = eurostat_url(dataset, query)
    response = fetch_json(url)
    ids = response.get("id", [])
    sizes = response.get("size", [])
    if "time" not in ids:
        return {"status": "gap", "geo": geo, "reason": "response has no time dimension", "url": url}
    if any(int(size) == 0 for size in sizes):
        return {"status": "gap", "geo": geo, "reason": "one or more dimensions returned no categories", "url": url}
    if not response.get("value"):
        return {"status": "gap", "geo": geo, "reason": "response has no numeric values", "url": url}

    values = {int(k): v for k, v in response["value"].items() if v is not None}
    time_index = response["dimension"]["time"]["category"]["index"]
    indexed_periods = sorted(((period, int(index)) for period, index in time_index.items()), key=lambda item: item[1], reverse=True)
    for period, index in indexed_periods:
        if index in values:
            return {
                "status": "ok",
                "geo": geo,
                "geo_label": dimension_label(response, "geo", geo),
                "period": period,
                "value": float(values[index]),
                "source_release_date": response.get("updated", ""),
                "url": url,
            }
    return {"status": "gap", "geo": geo, "reason": "no non-blank numeric value found", "url": url}


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if math.isnan(number):
        return ""
    return f"{number:.{digits}f}"


def signed_fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return ""
    number = float(value)
    sign = "+" if number > 0 else ""
    return f"{sign}{number:.{digits}f}"


def country_name(code: str, observations: dict[str, dict[str, Any]]) -> str:
    obs = observations.get(code)
    if obs and obs.get("geo_label"):
        return obs["geo_label"]
    return code


def main() -> int:
    registry = read_registry()
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict[str, str]] = []
    detail_for_summary: list[dict[str, Any]] = []

    for spec in SPECS:
        if spec.source_id not in registry:
            raise RuntimeError(f"Missing source_id in registry: {spec.source_id}")
        reg = registry[spec.source_id]
        observations: dict[str, dict[str, Any]] = {}
        gaps: dict[str, str] = {}
        for geo in ALL_GEOS:
            try:
                obs = latest_observation(spec.dataset_code, spec.query, geo)
            except Exception as exc:  # noqa: BLE001 - proof script should preserve per-geo gaps.
                obs = {"status": "gap", "geo": geo, "reason": f"{type(exc).__name__}: {exc}"}
            if obs["status"] == "ok":
                observations[geo] = obs
            else:
                gaps[geo] = obs.get("reason", "gap")
            time.sleep(0.05)

        benchmark = observations.get(BENCHMARK_GEO)
        if not benchmark:
            row = {
                "channel": spec.channel,
                "dataset_code": spec.dataset_code,
                "indicator_code": reg.get("indicator_code", ""),
                "unit": reg.get("unit", ""),
                "frequency": spec.frequency,
                "eu27_2020_period": "",
                "eu27_2020_value": "",
                "country_coverage_count": "0",
                "country_coverage_list": "",
                "missing_country_list": ",".join(EU27_COUNTRIES),
                "highest_positive_deviation_country": "",
                "highest_positive_deviation_value": "",
                "highest_positive_country_observation_value": "",
                "highest_negative_deviation_country": "",
                "highest_negative_deviation_value": "",
                "highest_negative_country_observation_value": "",
                "austria_period": observations.get("AT", {}).get("period", ""),
                "austria_value": fmt(observations.get("AT", {}).get("value")),
                "austria_deviation_vs_eu27_2020": "",
                "compatibility_note": f"STOP: EU27_2020 missing; gaps: {gaps.get(BENCHMARK_GEO, 'missing')}",
                "boundary_note": spec.boundary_note,
                "data_proof_decision": "STOP",
                "retrieved_at": retrieved_at,
                "source_release_date": "",
            }
            rows.append(row)
            detail_for_summary.append({"spec": spec, "row": row})
            continue

        benchmark_period = benchmark["period"]
        benchmark_value = benchmark["value"]
        compatible: list[dict[str, Any]] = []
        period_mismatches: list[str] = []
        missing: list[str] = []
        for geo in EU27_COUNTRIES:
            obs = observations.get(geo)
            if not obs:
                missing.append(geo)
                continue
            if obs["period"] != benchmark_period:
                period_mismatches.append(f"{geo}:{obs['period']}")
                continue
            compatible.append(
                {
                    "geo": geo,
                    "geo_label": obs["geo_label"],
                    "period": obs["period"],
                    "value": obs["value"],
                    "deviation": obs["value"] - benchmark_value,
                }
            )

        coverage_count = len(compatible)
        coverage_list = [item["geo"] for item in compatible]
        excluded_list = missing + period_mismatches
        austria_obs = observations.get("AT")
        austria_compatible = austria_obs is not None and austria_obs.get("period") == benchmark_period
        austria_deviation = (austria_obs["value"] - benchmark_value) if austria_compatible else None

        if compatible:
            highest_positive = max(compatible, key=lambda item: item["deviation"])
            highest_negative = min(compatible, key=lambda item: item["deviation"])
        else:
            highest_positive = None
            highest_negative = None

        if coverage_count >= 20 and austria_compatible:
            decision = "PASS"
        elif benchmark and coverage_count > 0:
            decision = "RESCOPE"
        else:
            decision = "STOP"

        compatibility_bits = [f"Compared countries use EU27_2020 period {benchmark_period} and {spec.frequency} frequency."]
        if period_mismatches:
            compatibility_bits.append(f"Excluded period mismatches: {', '.join(period_mismatches)}.")
        if missing:
            compatibility_bits.append(f"Missing country values: {', '.join(missing)}.")

        row = {
            "channel": spec.channel,
            "dataset_code": spec.dataset_code,
            "indicator_code": reg.get("indicator_code", ""),
            "unit": reg.get("unit", ""),
            "frequency": spec.frequency,
            "eu27_2020_period": benchmark_period,
            "eu27_2020_value": fmt(benchmark_value),
            "country_coverage_count": str(coverage_count),
            "country_coverage_list": ",".join(coverage_list),
            "missing_country_list": ",".join(excluded_list),
            "highest_positive_deviation_country": country_name(highest_positive["geo"], observations) if highest_positive else "",
            "highest_positive_deviation_value": signed_fmt(highest_positive["deviation"]) if highest_positive else "",
            "highest_positive_country_observation_value": fmt(highest_positive["value"]) if highest_positive else "",
            "highest_negative_deviation_country": country_name(highest_negative["geo"], observations) if highest_negative else "",
            "highest_negative_deviation_value": signed_fmt(highest_negative["deviation"]) if highest_negative else "",
            "highest_negative_country_observation_value": fmt(highest_negative["value"]) if highest_negative else "",
            "austria_period": austria_obs.get("period", "") if austria_obs else "",
            "austria_value": fmt(austria_obs.get("value")) if austria_obs else "",
            "austria_deviation_vs_eu27_2020": signed_fmt(austria_deviation) if austria_deviation is not None else "",
            "compatibility_note": " ".join(compatibility_bits),
            "boundary_note": spec.boundary_note,
            "data_proof_decision": decision,
            "retrieved_at": retrieved_at,
            "source_release_date": benchmark.get("source_release_date", ""),
        }
        rows.append(row)
        detail_for_summary.append({"spec": spec, "row": row})

    fieldnames = [
        "channel",
        "dataset_code",
        "indicator_code",
        "unit",
        "frequency",
        "eu27_2020_period",
        "eu27_2020_value",
        "country_coverage_count",
        "country_coverage_list",
        "missing_country_list",
        "highest_positive_deviation_country",
        "highest_positive_deviation_value",
        "highest_positive_country_observation_value",
        "highest_negative_deviation_country",
        "highest_negative_deviation_value",
        "highest_negative_country_observation_value",
        "austria_period",
        "austria_value",
        "austria_deviation_vs_eu27_2020",
        "compatibility_note",
        "boundary_note",
        "data_proof_decision",
        "retrieved_at",
        "source_release_date",
    ]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    pass_count = sum(1 for row in rows if row["data_proof_decision"] == "PASS")
    decision = "PROCEED TO INSIGHT PROOF" if pass_count >= 4 else "RESCOPE CHANNELS" if pass_count > 0 else "STOP"
    summary_lines = [
        "# V2 EU27 Extremes Data Proof Summary",
        "",
        "## Scope",
        "",
        "This proof tests whether selected official Eurostat channels can support an EU27 Macro Deviation Extremes Card showing where Austria sits relative to EU27_2020 and observed EU27 country extremes.",
        "",
        "No v1 data files, public docs, release files, tags, or repository settings are changed by this script.",
        "",
        "## Output",
        "",
        f"- CSV: `artifacts/{OUTPUT_CSV.name}`",
        f"- Retrieved at: `{retrieved_at}`",
        "",
        "## Channel Results",
        "",
        "| Channel | EU27_2020 period | Coverage | Highest positive deviation | Highest negative deviation | Austria deviation | Decision |",
        "|---|---:|---:|---|---|---:|---|",
    ]
    for item in detail_for_summary:
        row = item["row"]
        summary_lines.append(
            "| {channel} | {period} | {coverage}/27 | {pos} ({pos_dev}) | {neg} ({neg_dev}) | {at_dev} | {decision} |".format(
                channel=row["channel"],
                period=row["eu27_2020_period"] or "missing",
                coverage=row["country_coverage_count"],
                pos=row["highest_positive_deviation_country"] or "n/a",
                pos_dev=row["highest_positive_deviation_value"] or "n/a",
                neg=row["highest_negative_deviation_country"] or "n/a",
                neg_dev=row["highest_negative_deviation_value"] or "n/a",
                at_dev=row["austria_deviation_vs_eu27_2020"] or "n/a",
                decision=row["data_proof_decision"],
            )
        )
    summary_lines.extend(
        [
            "",
            "## Bounded Insight Check",
            "",
            "The proof is useful if at least four channels provide EU27_2020, Austria, at least 20 compatible EU27 country observations, and visible positive/negative deviations without aggregating across channels.",
            "",
            f"Current proof decision: **{decision}**.",
            "",
            "## Boundary",
            "",
            "The output identifies highest positive and highest negative deviations from EU27_2020 within each source-bounded channel. It does not classify countries, aggregate channels, or create advisory, predictive, diagnostic, market-use, or policy-use outputs.",
        ]
    )
    SUMMARY_MD.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"wrote {OUTPUT_CSV}")
    print(f"wrote {SUMMARY_MD}")
    print(f"pass_count={pass_count}")
    print(f"decision={decision}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
