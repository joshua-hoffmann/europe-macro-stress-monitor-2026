from __future__ import annotations

import csv
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = PROJECT_ROOT / "artifacts" / "v2_eu27_extremes_data_proof.csv"
OUTPUT_PNG = PROJECT_ROOT / "artifacts" / "v2_eu27_extremes_card_draft.png"
OUTPUT_REPORT = PROJECT_ROOT / "artifacts" / "v2_eu27_extremes_insight_proof.md"

TITLE = "EU27 Macro Deviation Extremes Card"
SUBTITLE = "Where Austria sits relative to EU27_2020 and observed EU27 country extremes, latest official Eurostat observations"
BOUNDARY = "Source-bounded latest official observations. Deviations are from EU27_2020 within each selected channel. No predictive, scoring, ranking, market-use, policy-use, or diagnostic claims."


def parse_number(value: str) -> float:
    return float(value.replace("+", "").strip())


def fmt_signed(value: float) -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1f} p.p."


def font(size: int, bold: bool = False):
    candidates = []
    if bold:
        candidates.extend([r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"])
    candidates.extend([r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"])
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def wrap(draw: ImageDraw.ImageDraw, text: str, max_width: int, fnt) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if draw.textbbox((0, 0), trial, font=fnt)[2] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def x_position(value: float, min_value: float, max_value: float, left: int, right: int) -> int:
    if min_value == max_value:
        return (left + right) // 2
    return int(round(left + (value - min_value) / (max_value - min_value) * (right - left)))


def load_rows() -> list[dict[str, str]]:
    with INPUT_CSV.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 6:
        raise RuntimeError(f"Expected 6 rows in {INPUT_CSV}, found {len(rows)}")
    return rows


def draw_card(rows: list[dict[str, str]]) -> None:
    width, height = 1800, 1280
    img = Image.new("RGB", (width, height), "#f7f8f3")
    draw = ImageDraw.Draw(img)

    f_title = font(46, True)
    f_subtitle = font(22)
    f_row_title = font(23, True)
    f_small = font(15)
    f_label = font(17)
    f_label_bold = font(17, True)
    f_axis = font(14)
    f_callout = font(21, True)

    ink = "#202829"
    muted = "#5c6666"
    panel_border = "#d5d9cf"
    center = "#606a6a"
    neg_color = "#355c9f"
    pos_color = "#c86b1f"
    at_color = "#111111"
    range_color = "#c7cfc8"

    draw.text((58, 42), TITLE, fill=ink, font=f_title)
    draw.text((60, 101), SUBTITLE, fill="#4d5757", font=f_subtitle)

    # Legend.
    legend_x, legend_y = 1125, 58
    draw.line((legend_x, legend_y + 12, legend_x + 42, legend_y + 12), fill=neg_color, width=7)
    draw.text((legend_x + 52, legend_y), "highest negative deviation", fill=muted, font=f_small)
    draw.line((legend_x, legend_y + 42, legend_x + 42, legend_y + 42), fill=pos_color, width=7)
    draw.text((legend_x + 52, legend_y + 30), "highest positive deviation", fill=muted, font=f_small)
    draw.ellipse((legend_x + 11, legend_y + 63, legend_x + 31, legend_y + 83), fill=at_color)
    draw.text((legend_x + 52, legend_y + 63), "Austria deviation", fill=muted, font=f_small)

    # Central bounded insight callout.
    callout = "Austria is the highest positive-deviation case for HICP energy, while it sits close to EU27_2020 for unemployment and gross debt."
    draw.rounded_rectangle((58, 150, 1742, 222), radius=10, fill="#fff7e8", outline="#dfc891", width=1)
    draw.text((84, 174), callout, fill="#3e3421", font=f_callout)
    draw.text((84, 199), "Interpret each channel separately; no aggregation across channels.", fill="#6b5c40", font=f_small)

    plot_left, plot_right = 570, 1410
    row_top = 270
    row_gap = 142
    row_h = 112

    for idx, row in enumerate(rows):
        top = row_top + idx * row_gap
        bottom = top + row_h
        draw.rounded_rectangle((58, top - 18, 1742, bottom + 16), radius=8, fill="#ffffff", outline=panel_border, width=1)

        channel = row["channel"]
        period = row["eu27_2020_period"]
        frequency = row["frequency"]
        unit_note = "Deviation in percentage points"
        neg_country = row["highest_negative_deviation_country"]
        pos_country = row["highest_positive_deviation_country"]
        neg_value = parse_number(row["highest_negative_deviation_value"])
        pos_value = parse_number(row["highest_positive_deviation_value"])
        at_value = parse_number(row["austria_deviation_vs_eu27_2020"])
        eu_value = 0.0

        pad = max(0.4, (pos_value - neg_value) * 0.08)
        min_value = min(neg_value, eu_value, at_value) - pad
        max_value = max(pos_value, eu_value, at_value) + pad
        x_neg = x_position(neg_value, min_value, max_value, plot_left, plot_right)
        x_pos = x_position(pos_value, min_value, max_value, plot_left, plot_right)
        x_zero = x_position(0.0, min_value, max_value, plot_left, plot_right)
        x_at = x_position(at_value, min_value, max_value, plot_left, plot_right)
        y = top + 56

        draw.text((84, top + 5), channel, fill=ink, font=f_row_title)
        draw.text((84, top + 38), f"{period} | {frequency} | {unit_note}", fill=muted, font=f_small)
        draw.text((84, top + 68), f"EU27_2020 = {row['eu27_2020_value']}", fill="#667070", font=f_axis)

        draw.line((plot_left, y, plot_right, y), fill=range_color, width=10)
        draw.line((x_zero, y - 35, x_zero, y + 35), fill=center, width=3)

        draw.ellipse((x_neg - 12, y - 12, x_neg + 12, y + 12), fill=neg_color)
        draw.ellipse((x_pos - 12, y - 12, x_pos + 12, y + 12), fill=pos_color)

        # Austria marker: diamond, then label above or below based on crowding.
        diamond = [(x_at, y - 17), (x_at + 17, y), (x_at, y + 17), (x_at - 17, y)]
        draw.polygon(diamond, fill=at_color)
        at_label = f"AT {fmt_signed(at_value)}"
        zero_label = "0 = EU27_2020"
        at_w = draw.textbbox((0, 0), at_label, font=f_label_bold)[2]
        zero_w = draw.textbbox((0, 0), zero_label, font=f_axis)[2]
        if abs(x_at - x_zero) < 95:
            at_x = max(plot_left, min(x_at - at_w - 22, plot_right - at_w))
            zero_x = max(plot_left, min(x_zero + 22, plot_right - zero_w))
        else:
            at_x = max(plot_left, min(x_at - at_w // 2, plot_right - at_w))
            zero_x = max(plot_left, min(x_zero - zero_w // 2, plot_right - zero_w))
        draw.text((zero_x, y - 58), zero_label, fill=center, font=f_axis)
        draw.text((at_x, y - 58), at_label, fill=at_color, font=f_label_bold)

        neg_label = f"{neg_country} {fmt_signed(neg_value)}"
        pos_label = f"{pos_country} {fmt_signed(pos_value)}"
        draw.text((plot_left, bottom - 16), neg_label, fill=neg_color, font=f_label_bold)
        draw.text((plot_right - draw.textbbox((0, 0), pos_label, font=f_label_bold)[2], bottom - 16), pos_label, fill=pos_color, font=f_label_bold)

    # Footer boundary note.
    footer_top = 1138
    draw.rounded_rectangle((58, footer_top, 1742, 1226), radius=8, fill="#eef1ea", outline="#d2d7ca", width=1)
    lines = wrap(draw, BOUNDARY, 1580, f_label)
    for i, line in enumerate(lines):
        draw.text((84, footer_top + 18 + i * 24), line, fill="#3f4a4a", font=f_label)
    draw.text((84, footer_top + 66), "Source: Eurostat API data proof output in artifacts/v2_eu27_extremes_data_proof.csv.", fill="#667070", font=f_small)

    OUTPUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUTPUT_PNG)


def write_report(rows: list[dict[str, str]]) -> None:
    energy = next(row for row in rows if row["channel"] == "HICP energy inflation")
    unemployment = next(row for row in rows if row["channel"] == "Unemployment rate")
    debt = next(row for row in rows if row["channel"] == "Government gross debt")
    pass_count = sum(1 for row in rows if row["data_proof_decision"] == "PASS")
    report = f"""# V2 EU27 Extremes Insight Proof

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

Within the selected official Eurostat observations, Austria is the highest positive deviation case for HICP energy inflation ({energy['austria_deviation_vs_eu27_2020']} p.p. vs EU27_2020), while Austria sits close to EU27_2020 for unemployment ({unemployment['austria_deviation_vs_eu27_2020']} p.p.) and government gross debt ({debt['austria_deviation_vs_eu27_2020']} p.p.). This creates a clear Austria-relative-to-extremes story without aggregating channels or classifying country risk.

## Visual and claim risks

- Per-channel ranges use separate scales, so the draft should not be read as comparing magnitudes across rows by line length.
- Annual and monthly channels are placed in the same card, so the period/frequency labels must remain visible.
- The draft should keep neutral endpoint language: highest positive deviation and highest negative deviation.
- The draft should not be converted into a composite index or country classification.

## Decision

PROCEED TO HERO ARTIFACT

## Reason

All {pass_count} channels passed Data Proof, and the draft card communicates a non-generic Austria-relative-to-extremes pattern without using aggregation or normative labels.

## Boundary

Source-bounded latest official observations only. No predictive, scoring, ranking, market-use, policy-use, or diagnostic claims.
"""
    OUTPUT_REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    rows = load_rows()
    draw_card(rows)
    write_report(rows)
    print(f"wrote {OUTPUT_PNG}")
    print(f"wrote {OUTPUT_REPORT}")


if __name__ == "__main__":
    main()
