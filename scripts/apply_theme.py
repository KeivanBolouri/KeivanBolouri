#!/usr/bin/env python3
"""
Odd UTC day  -> dark page background (#0D1117)
Even UTC day -> light page background (#FFFFFF)

GitHub strips HTML bgcolor/CSS from README HTML, so this writes a full-page
SVG (which GitHub DOES render) and points README.md at it. A daily Action
swaps the SVG + README automatically.
"""

from __future__ import annotations

import argparse
import html
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
ASSETS = ROOT / "assets"
PAGE_SVG = ASSETS / "page.svg"
ASSET_BASE = "https://raw.githubusercontent.com/KeivanBolouri/KeivanBolouri/main/assets"

TYPING_LINES = (
    "I'm+Keivan+Bolouri;"
    "I+am+interested+in;"
    "Causal+Machine+Learning;"
    "Causal+Inference;"
    "Optimization+in+Statistics;"
    "Statistical+Computing"
)


def colors(dark: bool) -> dict[str, str]:
    if dark:
        return {
            "label": "dark",
            "bg": "#0D1117",
            "ink": "#E6EDF3",
            "muted": "#C9D1D9",
            "typing": "58A6FF",
        }
    return {
        "label": "light",
        "bg": "#FFFFFF",
        "ink": "#1F2328",
        "muted": "#424A53",
        "typing": "0B3D91",
    }


def typing_src(c: dict[str, str]) -> str:
    bg = c["bg"].lstrip("#")
    return (
        "https://readme-typing-svg.demolab.com"
        f"?font=Righteous&amp;size=30&amp;center=true&amp;vCenter=true"
        f"&amp;width=820&amp;height=72&amp;duration=3000&amp;pause=1000"
        f"&amp;color={c['typing']}&amp;background={bg}"
        f"&amp;lines={TYPING_LINES}"
    )


def tx(x: int, y: int, size: int, fill: str, weight: str, anchor: str, text: str) -> str:
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{fill}" '
        f'font-family="Segoe UI, Helvetica, Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}">{html.escape(text)}</text>'
    )


def write_page_svg(c: dict[str, str]) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    bg, ink, muted = c["bg"], c["ink"], c["muted"]
    typing = typing_src(c)
    skills = "https://skillicons.dev/icons?i=r,python,cpp,cs,vscode,latex,git,github,java,html,anaconda,pycharm"
    snake = "https://raw.githubusercontent.com/salesp07/salesp07/output/github-contribution-grid-snake.svg"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="891" height="1450" viewBox="0 0 891 1450" role="img" aria-label="Keivan Bolouri ({c["label"]} theme)">',
        f'<rect width="891" height="1450" fill="{bg}"/>',
        tx(445, 64, 36, ink, "700", "middle", "Hi There!"),
        f'<image href="{typing}" xlink:href="{typing}" x="35" y="88" width="820" height="72" />',
        tx(40, 210, 22, ink, "700", "start", "Current Focus"),
        tx(40, 242, 15, muted, "400", "start", "Advanced training in causal machine learning, causal inference,"),
        tx(40, 264, 15, muted, "400", "start", "optimization in statistics, statistical computing, and reproducible"),
        tx(40, 286, 15, muted, "400", "start", "computational research workflows."),
        tx(40, 340, 22, ink, "700", "start", "Collaboration"),
        tx(40, 372, 15, muted, "400", "start", "Open to collaborations in causal inference, statistical machine learning,"),
        tx(40, 394, 15, muted, "400", "start", "and data-driven decision making for real-world applications."),
        tx(40, 448, 22, ink, "700", "start", "Methodological Expertise"),
        tx(40, 480, 15, muted, "400", "start", "Linear and generalized linear modeling, optimization in statistics,"),
        tx(40, 502, 15, muted, "400", "start", "statistical computing, machine learning algorithms, and statistical inference."),
        tx(445, 570, 20, ink, "700", "middle", "Languages, Frameworks, and Tools"),
        f'<image href="{skills}" xlink:href="{skills}" x="55" y="590" width="780" height="50" />',
        tx(445, 700, 20, ink, "700", "middle", "My Contributions"),
        f'<image href="{snake}" xlink:href="{snake}" x="40" y="720" width="810" height="180" />',
        tx(445, 960, 20, ink, "700", "middle", "Let's Connect"),
        tx(445, 1000, 14, muted, "400", "middle", "Website · Email · UCLA Email  (badges below)"),
        tx(445, 1410, 12, muted, "400", "middle", f"Automatic theme: {c['label']} page background (odd UTC day = dark, even = light)"),
        "</svg>",
    ]
    PAGE_SVG.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")


def write_readme(c: dict[str, str], day: int) -> None:
    bust = f"{day:02d}-{c['label']}"
    page = f"{ASSET_BASE}/page.svg?v={bust}"
    README.write_text(
        f"""<!-- theme:{c["label"]} utc_day:{day} odd=dark even=light -->
<p align="center">
  <img src="https://visitor-badge.laobi.icu/badge?page_id=KeivanBolouri.KeivanBolouri" alt="visitors" />
</p>

<!-- Full page background is an SVG (GitHub strips HTML bgcolor) -->
<p align="center">
  <img src="{page}" width="100%" alt="Keivan Bolouri — {c["label"]} page background" />
</p>

<p align="center">
  <a href="https://keivanbolouri.netlify.app">
    <img src="https://img.shields.io/badge/Website-keivanbolouri.netlify.app-brightgreen?style=flat-square&logo=google-chrome" alt="Website" />
  </a>
  <a href="mailto:keivan.bolouri.78@gmail.com">
    <img src="https://img.shields.io/badge/Email-keivan.bolouri.78@gmail.com-red?style=flat-square&logo=gmail" alt="Email" />
  </a>
  <a href="mailto:keivanbolouri@g.ucla.edu">
    <img src="https://img.shields.io/badge/UCLA%20Email-keivanbolouri@g.ucla.edu-2774AE?style=flat-square&logo=gmail&logoColor=white" alt="UCLA Email" />
  </a>
</p>
""",
        encoding="utf-8",
        newline="\n",
    )


def apply(day: int | None = None) -> str:
    now = datetime.now(timezone.utc)
    day = now.day if day is None else day
    dark = day % 2 == 1
    c = colors(dark)
    write_page_svg(c)
    write_readme(c, day)
    print(f"Applied {c['label']} SVG page background for UTC day {day}")
    return c["label"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=int, help="Override UTC day of month")
    args = parser.parse_args()
    apply(args.day)


if __name__ == "__main__":
    main()
