#!/usr/bin/env python3
"""
Every UTC day:
  odd  -> dark page bgcolor  (#0D1117)
  even -> light page bgcolor (#FFFFFF)

Keeps the normal HTML profile (Hi gif, typing, sections, tools, snake, links).
Does NOT use banner images or page SVG.

Note: GitHub may strip bgcolor when rendering; the workflow still updates
README.md every 24 hours so the source theme is always correct.
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "README.template.md"
README = ROOT / "README.md"

TYPING_LINES = (
    "I'm+Keivan+Bolouri;"
    "I+am+interested+in;"
    "Causal+Machine+Learning;"
    "Causal+Inference;"
    "Optimization+in+Statistics;"
    "Statistical+Computing"
)

TYPING_RE = re.compile(
    r'src="https://readme-typing-svg\.demolab\.com\?[^"]*"',
    re.IGNORECASE,
)


def apply(day: int | None = None) -> str:
    now = datetime.now(timezone.utc)
    day = now.day if day is None else day
    dark = day % 2 == 1
    label = "dark" if dark else "light"
    page_bg = "#0D1117" if dark else "#FFFFFF"
    typing_color = "58A6FF" if dark else "0B3D91"
    typing_bg = "0D1117" if dark else "FFFFFF"

    if not TEMPLATE.exists():
        raise SystemExit(f"Missing {TEMPLATE.name}")

    body = TEMPLATE.read_text(encoding="utf-8").strip() + "\n"

    typing_src = (
        "https://readme-typing-svg.demolab.com"
        f"?font=Righteous&amp;size=32&amp;center=true&amp;vCenter=true"
        f"&amp;width=900&amp;height=80&amp;duration=3000&amp;pause=1000"
        f"&amp;color={typing_color}&amp;background={typing_bg}"
        f"&amp;lines={TYPING_LINES}"
    )
    body, n = TYPING_RE.subn(f'src="{typing_src}"', body, count=1)
    if n != 1:
        raise SystemExit("Could not update typing SVG src in template")

    readme = f"""<!-- auto-theme: {label} · UTC day {day} · odd=dark even=light · every 24h -->
<table width="100%" cellpadding="18" cellspacing="0" border="0" bgcolor="{page_bg}">
<tr>
<td bgcolor="{page_bg}">

{body}
</td>
</tr>
</table>
"""
    README.write_text(readme, encoding="utf-8", newline="\n")
    print(f"Applied {label} bgcolor theme for UTC day {day}")
    return label


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=int)
    args = parser.parse_args()
    apply(args.day)


if __name__ == "__main__":
    main()
