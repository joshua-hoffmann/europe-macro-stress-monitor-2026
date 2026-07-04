from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = PROJECT_ROOT / "artifacts" / "v2_eu27_extremes_data_proof.csv"
OUTPUT_PNG = PROJECT_ROOT / "artifacts" / "eu27_macro_deviation_extremes_card.png"
OUTPUT_NOTES = PROJECT_ROOT / "artifacts" / "eu27_macro_deviation_extremes_card_notes.md"

TITLE = "EU27 Macro Deviation Extremes Card"
SUBTITLE = (
    "Where Austria sits relative to EU27_2020 and observed EU27 country extremes, "
    "latest official Eurostat observations"
)
CALLOUT = (
    "Austria is the highest positive-deviation case for HICP energy inflation, "
    "while it sits close to EU27_2020 for unemployment and government gross debt."
)
SCALE_NOTE = (
    "Each row uses its own scale; compare Austria's position within a row, "
    "not line lengths across rows."
)
FOOTER = (
    "Source-bounded latest official Eurostat observations. Deviations are from "
    "EU27_2020 within each channel. No aggregation, forecasts, scores, rankings, "
    "investment advice, policy advice, or diagnosis."
)

CHANNEL_ORDER = [
    "Real GDP growth",
    "HICP inflation",
    "HICP energy inflation",
    "Unemployment rate",
    "Government gross debt",
    "Government balance",
]


def parse_number(value: str) -> float:
    return float(value.replace("+", "").strip())


def fmt_signed(value: float) -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1f} p.p."


def fmt_value(value: str) -> str:
    return f"{parse_number(value):.1f}"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    if bold:
        candidates.extend(
            [
                r"C:\Windows\Fonts\segoeuib.ttf",
                r"C:\Windows\Fonts\arialbd.ttf",
            ]
        )
    candidates.extend(
        [
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arial.ttf",
        ]
    )
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0]


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(value, high))


def x_position(value: float, min_value: float, max_value: float, left: int, right: int) -> int:
    if min_value == max_value:
        return (left + right) // 2
    return int(round(left + (value - min_value) / (max_value - min_value) * (right - left)))


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    fnt: ImageFont.ImageFont,
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if text_width(draw, trial, fnt) <= max_width:
            current = trial
            continue
        if current:
            lines.append(current)
        current = word
    if current:
        lines.append(current)
    return lines


def load_rows() -> list[dict[str, str]]:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(INPUT_CSV)
    with INPUT_CSV.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 6:
        raise RuntimeError(f"Expected 6 source rows, found {len(rows)} in {INPUT_CSV}")

    rows_by_channel = {row["channel"]: row for row in rows}
    missing = [channel for channel in CHANNEL_ORDER if channel not in rows_by_channel]
    if missing:
        raise RuntimeError(f"Missing expected channels: {', '.join(missing)}")
    return [rows_by_channel[channel] for channel in CHANNEL_ORDER]


def draw_diamond(draw: ImageDraw.ImageDraw, x: int, y: int, radius: int, fill: str) -> None:
    draw.polygon(
        [
            (x, y - radius),
            (x + radius, y),
            (x, y + radius),
            (x - radius, y),
        ],
        fill=fill,
    )


def draw_row(
    draw: ImageDraw.ImageDraw,
    row: dict[str, str],
    idx: int,
    palette: dict[str, str],
    fonts: dict[str, ImageFont.ImageFont],
) -> None:
    panel_x0, panel_x1 = 64, 1936
    top = 365 + idx * 145
    height = 126
    bottom = top + height
    plot_left, plot_right = 655, 1590
    axis_y = top + 74

    draw.rounded_rectangle(
        (panel_x0, top, panel_x1, bottom),
        radius=9,
        fill=palette["panel"],
        outline=palette["border"],
        width=1,
    )

    neg_value = parse_number(row["highest_negative_deviation_value"])
    pos_value = parse_number(row["highest_positive_deviation_value"])
    at_value = parse_number(row["austria_deviation_vs_eu27_2020"])

    span = max(pos_value - neg_value, 1.0)
    pad = max(span * 0.08, 0.45)
    min_value = min(neg_value, 0.0, at_value) - pad
    max_value = max(pos_value, 0.0, at_value) + pad

    x_neg = x_position(neg_value, min_value, max_value, plot_left, plot_right)
    x_zero = x_position(0.0, min_value, max_value, plot_left, plot_right)
    x_at = x_position(at_value, min_value, max_value, plot_left, plot_right)
    x_pos = x_position(pos_value, min_value, max_value, plot_left, plot_right)

    draw.text((88, top + 19), row["channel"], fill=palette["ink"], font=fonts["row_title"])
    meta = (
        f"{row['eu27_2020_period']} | {row['frequency']} | "
        f"deviations in percentage points"
    )
    draw.text((88, top + 53), meta, fill=palette["muted"], font=fonts["small"])
    draw.text(
        (88, top + 82),
        f"EU27_2020 source value: {fmt_value(row['eu27_2020_value'])}",
        fill=palette["muted_2"],
        font=fonts["tiny"],
    )

    draw.line((plot_left, axis_y, plot_right, axis_y), fill=palette["range"], width=9)
    draw.line((x_zero, axis_y - 35, x_zero, axis_y + 35), fill=palette["zero"], width=3)

    draw.ellipse((x_neg - 11, axis_y - 11, x_neg + 11, axis_y + 11), fill=palette["negative"])
    draw.ellipse((x_pos - 11, axis_y - 11, x_pos + 11, axis_y + 11), fill=palette["positive"])
    draw_diamond(draw, x_at, axis_y, 18, palette["austria"])

    zero_label = "0 = EU27_2020"
    at_label = f"AT {fmt_signed(at_value)}"
    zero_w = text_width(draw, zero_label, fonts["axis"])
    at_w = text_width(draw, at_label, fonts["label_bold"])
    if abs(x_at - x_zero) < 105:
        zero_x = clamp(x_zero + 22, plot_left, plot_right - zero_w)
        at_x = clamp(x_at - at_w - 22, plot_left, plot_right - at_w)
        draw.text((zero_x, axis_y - 61), zero_label, fill=palette["zero"], font=fonts["axis"])
        draw.text((at_x, axis_y - 34), at_label, fill=palette["austria"], font=fonts["label_bold"])
    else:
        zero_x = clamp(x_zero - zero_w // 2, plot_left, plot_right - zero_w)
        at_x = clamp(x_at - at_w // 2, plot_left, plot_right - at_w)
        draw.text((zero_x, axis_y - 61), zero_label, fill=palette["zero"], font=fonts["axis"])
        draw.text((at_x, axis_y - 34), at_label, fill=palette["austria"], font=fonts["label_bold"])

    neg_label = (
        f"{row['highest_negative_deviation_country']} "
        f"{fmt_signed(neg_value)}"
    )
    pos_label = (
        f"{row['highest_positive_deviation_country']} "
        f"{fmt_signed(pos_value)}"
    )
    pos_w = text_width(draw, pos_label, fonts["label_bold"])
    draw.text((plot_left, bottom - 32), neg_label, fill=palette["negative"], font=fonts["label_bold"])
    draw.text(
        (plot_right - pos_w, bottom - 32),
        pos_label,
        fill=palette["positive"],
        font=fonts["label_bold"],
    )


def draw_card(rows: list[dict[str, str]]) -> None:
    width, height = 2000, 1450
    image = Image.new("RGB", (width, height), "#f7f6f0")
    draw = ImageDraw.Draw(image)

    fonts = {
        "title": font(54, True),
        "subtitle": font(24),
        "callout": font(26, True),
        "note": font(19),
        "legend": font(17),
        "legend_bold": font(17, True),
        "row_title": font(24, True),
        "small": font(16),
        "tiny": font(15),
        "axis": font(14),
        "label_bold": font(17, True),
        "footer": font(18),
    }
    palette = {
        "ink": "#1f292b",
        "muted": "#566264",
        "muted_2": "#687476",
        "panel": "#ffffff",
        "border": "#d8ddd4",
        "callout": "#fff7e6",
        "callout_border": "#dbc58e",
        "range": "#cbd2cc",
        "zero": "#646e70",
        "negative": "#315d8d",
        "positive": "#b46f2b",
        "austria": "#15191a",
        "footer": "#eef1eb",
    }

    draw.text((64, 46), TITLE, fill=palette["ink"], font=fonts["title"])
    draw.text((67, 116), SUBTITLE, fill=palette["muted"], font=fonts["subtitle"])

    draw.rounded_rectangle(
        (64, 165, 1936, 245),
        radius=10,
        fill=palette["callout"],
        outline=palette["callout_border"],
        width=1,
    )
    draw.text((90, 187), CALLOUT, fill="#3d3321", font=fonts["callout"])
    draw.text((90, 219), SCALE_NOTE, fill="#695d43", font=fonts["note"])

    legend_y = 282
    legend_x = 94
    draw.text((legend_x, legend_y - 3), "Legend", fill=palette["ink"], font=fonts["legend_bold"])
    item_x = legend_x + 92
    draw.ellipse((item_x, legend_y + 1, item_x + 18, legend_y + 19), fill=palette["negative"])
    draw.text((item_x + 30, legend_y - 1), "highest negative deviation", fill=palette["muted"], font=fonts["legend"])
    item_x += 325
    draw.line((item_x, legend_y + 10, item_x + 32, legend_y + 10), fill=palette["zero"], width=4)
    draw.text((item_x + 44, legend_y - 1), "EU27_2020 reference", fill=palette["muted"], font=fonts["legend"])
    item_x += 292
    draw_diamond(draw, item_x + 10, legend_y + 10, 11, palette["austria"])
    draw.text((item_x + 34, legend_y - 1), "Austria deviation from EU27_2020", fill=palette["muted"], font=fonts["legend"])
    item_x += 390
    draw.ellipse((item_x, legend_y + 1, item_x + 18, legend_y + 19), fill=palette["positive"])
    draw.text((item_x + 30, legend_y - 1), "highest positive deviation", fill=palette["muted"], font=fonts["legend"])
    draw.line((64, 325, 1936, 325), fill="#d9ddd5", width=1)

    for idx, row in enumerate(rows):
        draw_row(draw, row, idx, palette, fonts)

    footer_top = 1258
    draw.rounded_rectangle(
        (64, footer_top, 1936, 1386),
        radius=9,
        fill=palette["footer"],
        outline="#d1d7ce",
        width=1,
    )
    footer_lines = wrap_text(draw, FOOTER, 1748, fonts["footer"])
    for idx, line in enumerate(footer_lines):
        draw.text((90, footer_top + 22 + idx * 25), line, fill="#3f4a4b", font=fonts["footer"])
    source_line = "Source data used: artifacts/v2_eu27_extremes_data_proof.csv"
    draw.text((90, footer_top + 85), source_line, fill=palette["muted_2"], font=fonts["tiny"])
    draw.text((90, footer_top + 108), SCALE_NOTE, fill=palette["muted_2"], font=fonts["tiny"])

    OUTPUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT_PNG)


def write_notes(rows: list[dict[str, str]]) -> None:
    energy = next(row for row in rows if row["channel"] == "HICP energy inflation")
    unemployment = next(row for row in rows if row["channel"] == "Unemployment rate")
    debt = next(row for row in rows if row["channel"] == "Government gross debt")
    note = f"""# EU27 Macro Deviation Extremes Card Notes

## Source

- Source data used: `artifacts/v2_eu27_extremes_data_proof.csv`
- Output image: `artifacts/eu27_macro_deviation_extremes_card.png`
- Rows: {len(rows)}

## Bounded insight

Austria is the highest positive-deviation case for HICP energy inflation ({fmt_signed(parse_number(energy["austria_deviation_vs_eu27_2020"]))}), while it sits close to EU27_2020 for unemployment ({fmt_signed(parse_number(unemployment["austria_deviation_vs_eu27_2020"]))}) and government gross debt ({fmt_signed(parse_number(debt["austria_deviation_vs_eu27_2020"]))}).

## Reading boundary

- Each row uses its own scale; compare Austria's position within a row, not line lengths across rows.
- Deviations are percentage-point differences from EU27_2020 within the same channel.
- The card uses latest official Eurostat observations available in the v2 proof file.
- No aggregation, forecasts, scores, rankings, investment advice, policy advice, or diagnosis.
"""
    OUTPUT_NOTES.write_text(note, encoding="utf-8")


def main() -> None:
    rows = load_rows()
    draw_card(rows)
    write_notes(rows)
    print(f"Wrote {OUTPUT_PNG}")
    print(f"Wrote {OUTPUT_NOTES}")


if __name__ == "__main__":
    main()
