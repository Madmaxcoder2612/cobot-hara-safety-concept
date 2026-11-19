"""Generate the figures and the stopping distance table in docs/figures.

    docs/figures/coverage-matrix.svg
    docs/figures/stopping-distance.svg
    docs/figures/stopping-distance-table.md

The figures are plain SVG written by this script, so no plotting package is
needed. Run from the project folder:

    python tools/figures.py
"""

import math
from pathlib import Path
from xml.sax.saxutils import escape

from plr import PL_ORDER, highest_pl, required_pl
from stopping_distance import (DEFAULT_DECEL, DEFAULT_T_REACT, STOP_TIME_LIMIT, max_speed,
                               stopping_distance, stopping_time)
from traceability import load, split_ids

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "docs" / "figures"

PLR_COLOR = {"a": "#cfe3f7", "b": "#9ec5ee", "c": "#5b9bd5", "d": "#2a6db0", "e": "#14406e"}
INK = "#1f2933"
MUTED = "#6b7785"
SHORT_NAME = {"SF-01": "E-stop", "SF-02": "PFL", "SF-03": "SLS", "SF-04": "SLP",
              "SF-05": "Standstill", "SF-06": "Enabling", "SF-07": "Brakes"}


def text(x, y, s, size=13, anchor="start", weight="normal", fill=INK, extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}" fill="{fill}" {extra}>{escape(s)}</text>')


def ink_for(pl):
    return "#ffffff" if pl in "cde" else INK


def svg_open(width, height, title, description):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" font-family="Segoe UI, Helvetica, Arial, sans-serif" '
            f'role="img" aria-labelledby="t d"><title id="t">{escape(title)}</title>'
            f'<desc id="d">{escape(description)}</desc>'
            f'<rect width="{width}" height="{height}" fill="#ffffff"/>')


def coverage_svg(hazards, functions):
    label_w, plr_w, cell_w, other_w = 290, 56, 72, 200
    pad, top, row_h = 20, 100, 30
    n_h, n_sf = len(hazards), len(functions)
    width = pad * 2 + label_w + plr_w + n_sf * cell_w + other_w
    height = top + n_h * row_h + 12 + 2 * row_h + 80
    x0 = pad + label_w + plr_w

    plr_of = {hz["id"]: required_pl(hz["S"], hz["F"], hz["P"]) for hz in hazards}
    in_column = {sf["id"]: [] for sf in functions}
    for hz in hazards:
        for sf_id in split_ids(hz["safety_functions"]):
            in_column[sf_id].append(plr_of[hz["id"]])

    out = [svg_open(width, height, "Which safety function covers which hazard",
                    "Matrix of 12 hazards against 7 safety functions. Cell colour is the required "
                    "Performance Level of the hazard. The bottom rows compare the highest required "
                    "level in each column with the target level of the function."),
           text(pad, 30, "Which safety function covers which hazard", 18, weight="bold"),
           text(pad, 52, "Cell colour and letter: required Performance Level (PLr) of the hazard",
                12, fill=MUTED)]

    out.append(text(pad + 4, top - 12, "Hazard", 12, weight="bold", fill=MUTED))
    out.append(text(pad + label_w + plr_w / 2, top - 12, "PLr", 12, "middle", "bold", MUTED))
    for j, sf in enumerate(functions):
        cx = x0 + j * cell_w + cell_w / 2
        out.append(text(cx, top - 38, sf["id"], 12, "middle", "bold"))
        out.append(text(cx, top - 22, SHORT_NAME.get(sf["id"], sf["name"]), 11, "middle", fill=MUTED))
    out.append(text(x0 + n_sf * cell_w + 12, top - 12, "Other measures", 12, weight="bold", fill=MUTED))

    for i, hz in enumerate(hazards):
        y = top + i * row_h
        if i % 2 == 0:
            out.append(f'<rect x="{pad}" y="{y}" width="{width - 2 * pad}" height="{row_h}" fill="#f5f7fa"/>')
        linked = split_ids(hz["safety_functions"])
        out.append(text(pad + 4, y + 20, f"{hz['id']}  {hz['hazard']}", 13))
        out.append(text(pad + label_w + plr_w / 2, y + 20,
                        plr_of[hz["id"]].upper() if linked else "–", 13, "middle",
                        "bold", INK if linked else MUTED))
        for j, sf in enumerate(functions):
            if sf["id"] in linked:
                pl = plr_of[hz["id"]]
                cx = x0 + j * cell_w
                out.append(f'<rect x="{cx + 6}" y="{y + 4}" width="{cell_w - 12}" height="{row_h - 8}" '
                           f'rx="4" fill="{PLR_COLOR[pl]}"/>')
                out.append(text(cx + cell_w / 2, y + 20, pl.upper(), 13, "middle", "bold", ink_for(pl)))
        if not linked:
            out.append(text(x0 + n_sf * cell_w + 12, y + 20, "design / information only", 12,
                            fill=MUTED, extra='font-style="italic"'))

    ys = top + n_h * row_h + 12
    out.append(f'<line x1="{pad}" y1="{ys - 6}" x2="{width - pad}" y2="{ys - 6}" stroke="#c7ced6"/>')
    rows = (("Highest PLr in column", lambda sf: highest_pl(in_column[sf]) if in_column[sf] else None),
            ("Target PL of function", lambda sf: next(f["pl_target"] for f in functions if f["id"] == sf)))
    for k, (label, pick) in enumerate(rows):
        y = ys + k * row_h
        out.append(text(pad + 4, y + 20, label, 13, weight="bold"))
        for j, sf in enumerate(functions):
            pl = pick(sf["id"])
            if pl:
                cx = x0 + j * cell_w
                out.append(f'<rect x="{cx + 6}" y="{y + 4}" width="{cell_w - 12}" height="{row_h - 8}" '
                           f'rx="4" fill="{PLR_COLOR[pl]}"/>')
                out.append(text(cx + cell_w / 2, y + 20, pl.upper(), 13, "middle", "bold", ink_for(pl)))

    ly = ys + 2 * row_h + 28
    used = sorted({pl for pls in in_column.values() for pl in pls}, key=PL_ORDER.index)
    lx = pad + 4
    out.append(text(lx, ly + 4, "Legend:", 12, fill=MUTED))
    lx += 56
    for pl in used:
        out.append(f'<rect x="{lx}" y="{ly - 9}" width="18" height="18" rx="3" fill="{PLR_COLOR[pl]}"/>')
        out.append(text(lx + 26, ly + 4, f"PL {pl}", 12))
        lx += 80
    out.append(text(pad + 4, ly + 30,
                    "A function must meet the highest PLr in its column. Target PL d with PLr c is "
                    "allowed (higher than needed), the reverse never is.", 11, fill=MUTED))
    out.append("</svg>")
    return "\n".join(out)


def stopping_svg():
    w, h = 760, 450
    ml, mr, mt, mb = 84, 40, 64, 84
    pw, ph = w - ml - mr, h - mt - mb
    vmax = 2.0
    dmax = math.ceil(stopping_distance(vmax) * 10) / 10

    def px(v):
        return ml + v / vmax * pw

    def py(d):
        return mt + ph - d / dmax * ph

    out = [svg_open(w, h, "Stopping distance against tool speed",
                    "Line chart of the distance the robot tool travels after a stop command for tool "
                    f"speeds from 0 to {vmax} metres per second, with the collaborative speed limit marked."),
           text(ml, 30, "Stopping distance grows faster than speed", 18, weight="bold"),
           text(ml, 50, "Distance travelled by the tool after the stop command", 12, fill=MUTED)]

    steps = int(round(dmax * 10))
    for i in range(steps + 1):
        d = i / 10
        out.append(f'<line x1="{ml}" y1="{py(d):.1f}" x2="{ml + pw}" y2="{py(d):.1f}" stroke="#e3e8ee"/>')
        out.append(text(ml - 10, py(d) + 4, f"{d * 1000:.0f}", 12, "end", fill=MUTED))
    for i in range(int(vmax * 2) + 1):
        v = i / 2
        out.append(f'<line x1="{px(v):.1f}" y1="{mt + ph}" x2="{px(v):.1f}" y2="{mt + ph + 5}" stroke="{MUTED}"/>')
        out.append(text(px(v), mt + ph + 22, f"{v:.1f}", 12, "middle", fill=MUTED))
    out.append(f'<line x1="{ml}" y1="{mt + ph}" x2="{ml + pw}" y2="{mt + ph}" stroke="{MUTED}"/>')
    out.append(f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt + ph}" stroke="{MUTED}"/>')
    out.append(text(ml + pw / 2, h - 36, "Tool speed [m/s]", 13, "middle"))
    out.append(text(22, mt + ph / 2, "Stopping distance [mm]", 13, "middle",
                    extra=f'transform="rotate(-90 22 {mt + ph / 2})"'))

    limit = 0.25
    out.append(f'<line x1="{px(limit):.1f}" y1="{mt}" x2="{px(limit):.1f}" y2="{mt + ph}" '
               f'stroke="{PLR_COLOR["d"]}" stroke-dasharray="5 4"/>')
    points = " ".join(f"{px(i * 0.02):.1f},{py(stopping_distance(i * 0.02)):.1f}"
                      for i in range(int(vmax / 0.02) + 1))
    out.append(f'<polyline points="{points}" fill="none" stroke="{PLR_COLOR["e"]}" stroke-width="3"/>')

    d_limit, d_full = stopping_distance(limit), stopping_distance(vmax)
    out.append(f'<circle cx="{px(limit):.1f}" cy="{py(d_limit):.1f}" r="5" fill="{PLR_COLOR["d"]}"/>')
    out.append(text(px(limit) + 8, mt + 16, "250 mm/s (collaborative limit)", 12, weight="bold"))
    out.append(text(px(limit) + 12, py(d_limit) + 20, f"{d_limit * 1000:.0f} mm", 12))
    out.append(f'<circle cx="{px(vmax):.1f}" cy="{py(d_full):.1f}" r="5" fill="{PLR_COLOR["d"]}"/>')
    out.append(text(px(vmax) - 12, py(d_full) - 22, "2 m/s (full speed)", 12, "end", "bold"))
    out.append(text(px(vmax) - 12, py(d_full) - 6, f"{d_full * 1000:.0f} mm", 12, "end"))

    out.append(text(ml, h - 12, f"Model: reaction time {DEFAULT_T_REACT} s, constant deceleration "
                    f"{DEFAULT_DECEL} m/s². Assumed values, not measured.", 11, fill=MUTED))
    out.append("</svg>")
    return "\n".join(out)


def stopping_table_md():
    lines = ["# Stopping distance table", "",
             "Generated by `tools/figures.py`. Do not edit by hand.", "",
             f"Model: reaction time {DEFAULT_T_REACT} s, constant deceleration {DEFAULT_DECEL} m/s². "
             "Both values are assumptions for this fictional cell.", "",
             "## Distance and time at a given speed", "",
             f"| Speed | Stopping distance | Stopping time | SR-04 (at most {STOP_TIME_LIMIT * 1000:.0f} ms) |",
             "|---|---|---|---|"]
    for v in (0.1, 0.25, 0.5, 1.0, 1.5, 2.0):
        t = stopping_time(v)
        lines.append(f"| {v * 1000:.0f} mm/s | {stopping_distance(v) * 1000:.0f} mm | "
                     f"{t * 1000:.0f} ms | {'met' if t <= STOP_TIME_LIMIT else 'not met'} |")
    lines += ["", "## Highest speed that still stops within a given distance", "",
              "| Distance available | Highest speed |", "|---|---|"]
    for d_mm in (25, 50, 100, 200, 500):
        lines.append(f"| {d_mm} mm | {max_speed(d_mm / 1000) * 1000:.0f} mm/s |")
    lines.append("")
    return "\n".join(lines)


def write(name, content):
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / name).write_text(content, encoding="utf-8", newline="\n")


def main():
    hazards = load("hazards.csv")
    functions = load("safety_functions.csv")
    write("coverage-matrix.svg", coverage_svg(hazards, functions))
    write("stopping-distance.svg", stopping_svg())
    write("stopping-distance-table.md", stopping_table_md())
    print(f"Wrote 3 files to {FIG}")


if __name__ == "__main__":
    main()
