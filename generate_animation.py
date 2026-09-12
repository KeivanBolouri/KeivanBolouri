"""Generate a reproducible association illustration for a GitHub README.

Dependencies: numpy, matplotlib, Pillow. Run: python generate_animation.py
This is deliberately selective omission (largest Y first), not a comparison of
causal estimators or a result from a research project. The underlying data remain
fixed; at every step the blue OLS line is refitted to the retained observations.
"""

from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image, ImageDraw, ImageFont
import numpy as np


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
QA = ROOT / "qa"
ASSETS.mkdir(exist_ok=True)
QA.mkdir(exist_ok=True)

BG = "#f6f8fc"
INK = "#172c48"
MUTED = "#61748a"
BLUE = "#087ecc"
PURPLE = "#8064c6"
FADED = "#dce3ed"

rng = np.random.default_rng(2026)
n = 120
x = rng.uniform(-2.5, 2.5, n)
y = 0.75 * x + rng.normal(0, 1.25, n)
omit_order = np.argsort(y)[::-1]
full_fit = np.polyfit(x, y, 1)
grid = np.linspace(-2.65, 2.65, 200)

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 12,
    "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
    "text.color": INK, "axes.linewidth": 0.8,
})
fig = plt.figure(figsize=(9.6, 4.8), dpi=100, facecolor=BG)
fig.text(.064, .915, "What changes when data go missing?", fontsize=22, weight="bold")
fig.text(.064, .857, "One dataset. Selective omissions. A different fitted relationship.",
         fontsize=12.4, color=MUTED)
ax = fig.add_axes([.085, .25, .605, .535], facecolor="white")
ax.set_xlim(-2.75, 2.75)
ax.set_ylim(-4.7, 4.7)
ax.set_xticks([-2, -1, 0, 1, 2])
ax.set_yticks([-4, -2, 0, 2, 4])
ax.set_xlabel("Predictor (X)", labelpad=7)
ax.set_ylabel("Outcome (Y)", labelpad=8)
ax.grid(color="#e9edf3", linewidth=.8)
ax.set_axisbelow(True)
for side in ["top", "right"]:
    ax.spines[side].set_visible(False)
for side in ["bottom", "left"]:
    ax.spines[side].set_color("#ced7e3")

# Omitted points remain faintly visible so the selection process is legible.
omitted = ax.scatter([], [], s=27, color=FADED, edgecolors="none", zorder=2)
retained = ax.scatter(x, y, s=31, color=BLUE, edgecolors="white", linewidth=.5,
                      alpha=.8, zorder=3)
ax.plot(grid, np.polyval(full_fit, grid), color=PURPLE, linewidth=2.4,
        linestyle=(0, (4, 3)), zorder=4)
current_line, = ax.plot(grid, np.polyval(full_fit, grid), color=BLUE,
                        linewidth=2.7, zorder=5)

fig.text(.748, .72, "OBSERVATIONS RETAINED", fontsize=9.7, weight="bold", color=MUTED)
count_text = fig.text(.748, .638, "120 / 120", fontsize=26, weight="bold")
missing_text = fig.text(.75, .585, "0% omitted", fontsize=12.5, color=MUTED)
fig.text(.748, .478, "FITTED SLOPE", fontsize=10, weight="bold", color=MUTED)
slope_text = fig.text(.748, .402, f"{full_fit[0]:.2f}", fontsize=27,
                     weight="bold", color=BLUE)
fig.text(.75, .35, f"Full data: {full_fit[0]:.2f}", fontsize=12, color=PURPLE)
fig.text(.748, .175, "Higher outcomes are\nomitted first. Faded dots\nshow omitted observations.",
         fontsize=10.5, color=MUTED, linespacing=1.5)

fig.legend(handles=[
    Line2D([0], [0], color=PURPLE, lw=2.4, linestyle=(0, (4, 3)), label="Full-data fit"),
    Line2D([0], [0], color=BLUE, lw=2.7, label="Retained-data fit")],
    loc="center", bbox_to_anchor=(.393, .092), ncol=2, frameon=False,
    fontsize=11, handlelength=2.7, columnspacing=2)
fig.text(.5, .025, "Simulated data  |  Regression association only",
         ha="center", fontsize=10.4, color=MUTED)

frames = []
slopes = []
for removed in range(61):
    keep = np.ones(n, dtype=bool)
    keep[omit_order[:removed]] = False
    coef = np.polyfit(x[keep], y[keep], 1)
    slopes.append(float(coef[0]))
    retained.set_offsets(np.column_stack([x[keep], y[keep]]))
    omitted.set_offsets(np.column_stack([x[~keep], y[~keep]]))
    current_line.set_ydata(np.polyval(coef, grid))
    count_text.set_text(f"{n-removed} / {n}")
    missing_text.set_text(f"{removed/n:.0%} omitted")
    slope_text.set_text(f"{coef[0]:.2f}")
    fig.canvas.draw()
    frame = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())).convert("RGB")
    frames.append(frame)
plt.close(fig)

# Shared palette avoids color flicker. The reverse sequence restores the data
# before looping; pauses make both endpoints readable without a jump cut.
palette = frames[0].quantize(colors=192, method=Image.Quantize.MEDIANCUT)
indexed = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
sequence = indexed + indexed[-2:0:-1]
duration = [80] * len(sequence)
duration[0] = 1200
duration[60] = 1800
out = ASSETS / "missing-data-simulation.gif"
sequence[0].save(out, save_all=True, append_images=sequence[1:], duration=duration,
                 loop=0, optimize=True, disposal=1)

for k, name in [(0, "full-data"), (30, "25-percent-omitted"), (60, "50-percent-omitted")]:
    frames[k].save(QA / f"{name}.png")
sheet = Image.new("RGB", (960, 1440), BG)
for j, k in enumerate([0, 30, 60]):
    sheet.paste(frames[k], (0, j * 480))
sheet.save(QA / "animation-contact-sheet.png")

with Image.open(out) as check:
    durations = []
    hashes = set()
    for i in range(check.n_frames):
        check.seek(i)
        durations.append(check.info.get("duration", 0))
        hashes.add(hash(check.convert("RGB").tobytes()))
    report = {
        "size_px": list(check.size), "frames": check.n_frames,
        "distinct_frames": len(hashes), "loop": check.info.get("loop"),
        "duration_seconds": sum(durations)/1000, "size_bytes": out.stat().st_size,
        "seed": 2026, "full_slope": slopes[0], "final_slope": slopes[-1],
        "selection": "Omit observations in descending order of Y, then restore them.",
        "claim": "Illustrative OLS association, not a causal effect estimate.",
    }
    assert check.n_frames > 60 and len(hashes) > 50
    assert report["loop"] == 0
    assert abs(slopes[0]-slopes[-1]) > .2
    assert out.stat().st_size < 3_000_000
    (QA / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
