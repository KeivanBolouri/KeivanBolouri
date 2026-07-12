#!/usr/bin/env python3
"""Odd day = dark page bgcolor, even day = light page bgcolor (HTML only, no banners)."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

THEME_RE = re.compile(r"<!--THEME_START-->.*?<!--THEME_END-->", re.DOTALL)

TYPING_LINES = (
    "I'm+Keivan+Bolouri;"
    "I+am+interested+in;"
    "Causal+Machine+Learning;"
    "Causal+Inference;"
    "Optimization+in+Statistics;"
    "Statistical+Computing"
)


def theme_block(dark: bool) -> str:
    if dark:
        bg = "#0D1117"
        ink = "#E6EDF3"
        muted = "#C9D1D9"
        typing = "58A6FF"
        label = "dark"
    else:
        bg = "#FFFFFF"
        ink = "#1F2328"
        muted = "#424A53"
        typing = "0B3D91"
        label = "light"

    typing_src = (
        "https://readme-typing-svg.demolab.com"
        f"?font=Righteous&amp;size=32&amp;center=true&amp;vCenter=true"
        f"&amp;width=900&amp;height=80&amp;duration=3000&amp;pause=1000"
        f"&amp;color={typing}&amp;lines={TYPING_LINES}"
    )

    # One full-width table: this is the README "page" background via HTML code.
    return f"""<!--THEME_START-->
<!-- theme: {label} -->
<table width="100%" cellpadding="22" cellspacing="0" border="0" bgcolor="{bg}">
<tr>
<td bgcolor="{bg}">

<p align="center">
  <img src="https://visitor-badge.laobi.icu/badge?page_id=KeivanBolouri.KeivanBolouri"/>
</p>

<h1 align="center">
  <font color="{ink}">Hi There!</font>
  <img
    src="https://raw.githubusercontent.com/ABSphreak/ABSphreak/master/gifs/Hi.gif"
    width="40"
    alt="waving hand"
  />
</h1>

<p align="center">
  <img src="{typing_src}" alt="Typing SVG" />
</p>

<h3><font color="{ink}">🌱 Current Focus</font></h3>
<p>
  <font color="{muted}">
  Advanced training in
  <code>causal machine learning</code>,
  <code>causal inference</code>,
  <code>optimization in statistics</code>,
  <code>statistical computing</code>,
  and reproducible computational research workflows.
  </font>
</p>

<h3><font color="{ink}">👯 Collaboration</font></h3>
<p>
  <font color="{muted}">
  Open to collaborations in
  <code>causal inference</code>,
  <code>statistical machine learning</code>,
  and data-driven decision making for real-world applications.
  </font>
</p>

<h3><font color="{ink}">💬 Methodological Expertise</font></h3>
<p>
  <font color="{muted}">
  <code>Linear and generalized linear modeling</code>,
  <code>optimization in statistics</code>,
  <code>statistical computing</code>,
  <code>machine learning algorithms</code>,
  and
  <code>statistical inference</code>.
  </font>
</p>

<br/>
<hr/>

<h2 align="center"><font color="{ink}">⚒️ Languages, Frameworks, and Tools ⚒️</font></h2>
<div align="center">
  <img src="https://skillicons.dev/icons?i=r,python,cpp,cs,vscode,latex,git,github,java,html,anaconda,pycharm" alt="Languages and tools" />
</div>

<hr/>

<div align="center">
  <h2><font color="{ink}">🐍 My Contributions 🐍</font></h2>
  <br/>
  <img alt="snake eating my contributions" src="https://raw.githubusercontent.com/salesp07/salesp07/output/github-contribution-grid-snake.svg" />
  <br/><br/><br/>
</div>

<hr/>

<h2><font color="{ink}">🤝 Let’s Connect</font></h2>

<p>
  <a href="https://keivanbolouri.netlify.app">
    <img src="https://img.shields.io/badge/Website-keivanbolouri.netlify.app-brightgreen?style=flat-square&amp;logo=google-chrome" alt="Website" />
  </a>
  <a href="mailto:keivan.bolouri.78@gmail.com">
    <img src="https://img.shields.io/badge/Email-keivan.bolouri.78@gmail.com-red?style=flat-square&amp;logo=gmail" alt="Email" />
  </a>
  <a href="mailto:keivanbolouri@g.ucla.edu">
    <img src="https://img.shields.io/badge/UCLA%20Email-keivanbolouri@g.ucla.edu-2774AE?style=flat-square&amp;logo=gmail&amp;logoColor=white" alt="UCLA Email" />
  </a>
</p>

</td>
</tr>
</table>
<!--THEME_END-->
"""


def apply(day: int | None = None) -> str:
    now = datetime.now(timezone.utc)
    day = now.day if day is None else day
    dark = day % 2 == 1
    block = theme_block(dark).strip() + "\n"
    README.write_text(block, encoding="utf-8", newline="\n")
    mode = "dark" if dark else "light"
    print(f"Applied full-page {mode} bgcolor for UTC day {day}")
    return mode


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=int)
    args = parser.parse_args()
    apply(args.day)


if __name__ == "__main__":
    main()
