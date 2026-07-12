#!/usr/bin/env python3
"""Apply odd-day dark / even-day light theme blocks in README.md."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

# Profile READMEs require absolute image URLs (relative paths = "Invalid image source")
ASSET_BASE = "https://raw.githubusercontent.com/KeivanBolouri/KeivanBolouri/main/assets"

THEME_RE = re.compile(
    r"<!--THEME_START-->.*?<!--THEME_END-->",
    re.DOTALL,
)

TYPING_LINES = (
    "I'm+Keivan+Bolouri;"
    "I+am+interested+in;"
    "Causal+Machine+Learning;"
    "Causal+Inference;"
    "Optimization+in+Statistics;"
    "Statistical+Computing"
)


def theme_block(dark: bool) -> str:
    banner = f"{ASSET_BASE}/banner-{'dark' if dark else 'light'}.png"
    if dark:
        color = "58A6FF"
        background = "0D1117"
        label = "dark"
    else:
        color = "0B3D91"
        background = "FFFFFF"
        label = "light"

    typing = (
        "https://readme-typing-svg.demolab.com"
        f"?font=Righteous&amp;size=32&amp;center=true&amp;vCenter=true"
        f"&amp;width=900&amp;height=80&amp;duration=3000&amp;pause=1000"
        f"&amp;color={color}&amp;background={background}"
        f"&amp;lines={TYPING_LINES}"
    )

    return f"""<!--THEME_START-->
<!-- theme: {label} -->
<p align="center">
  <img src="{banner}" width="100%" alt="profile theme banner ({label})" />
</p>

<h1 align="center">
  Hi There!
  <img
    src="https://raw.githubusercontent.com/ABSphreak/ABSphreak/master/gifs/Hi.gif"
    width="40"
    alt="waving hand"
  />
</h1>

<p align="center">
  <img
    src="{typing}"
    alt="Typing SVG"
  />
</p>
<!--THEME_END-->"""


def apply(day: int | None = None) -> str:
    now = datetime.now(timezone.utc)
    day = now.day if day is None else day
    dark = day % 2 == 1  # odd -> dark/black, even -> light/white
    block = theme_block(dark)

    text = README.read_text(encoding="utf-8")
    if not THEME_RE.search(text):
        raise SystemExit("README.md is missing <!--THEME_START--> ... <!--THEME_END--> markers")

    updated = THEME_RE.sub(block, text)
    README.write_text(updated, encoding="utf-8", newline="\n")
    mode = "dark" if dark else "light"
    print(f"Applied {mode} theme for UTC day {day}")
    return mode


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=int, help="Override day of month (for testing)")
    args = parser.parse_args()
    apply(args.day)


if __name__ == "__main__":
    main()
