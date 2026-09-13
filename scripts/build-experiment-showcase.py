#!/usr/bin/env python3
"""Package existing scientific GIFs into one GitHub-compatible 55-second loop.

Run from any directory. Source labels and chart data are preserved: every source
is sampled across its full duration, uniformly resized, and letterboxed. The
output has 20 frames per experiment at 250 ms each, so every experiment receives
exactly 5 seconds. A progress bar keeps otherwise identical frames distinct.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
OUTPUT = ASSETS / 'experiments-showcase.gif'
PREVIEW = ROOT / 'preview' / 'experiments-showcase-contact-sheet.png'
WIDTH, HEIGHT = 800, 640
FRAME_MS, FRAMES_PER_EXPERIMENT = 250, 20
BACKGROUND = '#12243b'
TEXT = '#eef3fb'
MUTED = '#b6c6d9'
ACCENT = '#86e1d5'
EXPERIMENTS = [
    ('lasso-coefficients.gif', 'Lasso variable selection'),
    ('monte-carlo-card.gif', 'Monte Carlo integration'),
    ('missing-data-simulation.gif', 'Missing observations'),
    ('bootstrap-sampling.gif', 'Bootstrap sampling'),
    ('confidence-intervals.gif', 'Confidence intervals'),
    ('federated-learning.gif', 'Federated learning'),
    ('gradient-descent.gif', 'Gradient descent'),
    ('confounding-adjustment.gif', 'Confounding and adjustment'),
    ('observation-intervention.gif', 'Observation vs. intervention'),
    ('bayesian-updating.gif', 'Bayesian updating'),
    ('mcmc-sampling.gif', 'MCMC sampling'),
]


def font(size: int, bold: bool = False):
    filename = 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    path = Path('/usr/share/fonts/truetype/dejavu') / filename
    return ImageFont.truetype(str(path) if path.exists() else filename, size)


def source_frames(path: Path):
    """Decode composited source frames with their actual presentation times."""
    frames, cumulative, total = [], [], 0
    with Image.open(path) as image:
        for index in range(image.n_frames):
            image.seek(index)
            frames.append(image.convert('RGB'))
            total += int(image.info.get('duration', 100))
            cumulative.append(total)
    return frames, cumulative, total


def create_frame(source: Image.Image, experiment: int, frame: int) -> Image.Image:
    canvas = Image.new('RGB', (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    draw.text((22, 12), 'STATISTICAL EXPERIMENTS', font=font(11, True), fill=ACCENT)
    draw.text((WIDTH - 24, 18), f'{experiment + 1} / {len(EXPERIMENTS)}',
              font=font(15, True), fill=MUTED, anchor='ra')
    draw.text((22, 32), EXPERIMENTS[experiment][1], font=font(23, True), fill=TEXT)
    # Uniform scaling only. Full source including every label remains visible.
    fitted = ImageOps.contain(source, (768, 536), Image.Resampling.LANCZOS)
    x = (WIDTH - fitted.width) // 2
    y = 68 + (536 - fitted.height) // 2
    canvas.paste(fitted, (x, y))
    draw.text((22, 614), 'Changes every 5 seconds · Click to explore',
              font=font(12), fill=MUTED)
    for number in range(len(EXPERIMENTS)):
        cx = 650 + number * 12
        draw.ellipse((cx, 618, cx + 5, 623),
                     fill=ACCENT if number == experiment else '#496078')
    # Fill is tied to presentation frames, not a browser or server timer.
    draw.rectangle((0, HEIGHT - 3, WIDTH, HEIGHT - 1), fill='#263e56')
    progress = round(WIDTH * (frame + 1) / FRAMES_PER_EXPERIMENT)
    draw.rectangle((0, HEIGHT - 3, progress - 1, HEIGHT - 1), fill=ACCENT)
    return canvas


def main():
    output_frames = []
    source_report = []
    for experiment, (filename, title) in enumerate(EXPERIMENTS):
        originals, ends, duration = source_frames(ASSETS / filename)
        selected = []
        for frame in range(FRAMES_PER_EXPERIMENT):
            # Include both the first and final source frames; interior samples
            # follow the original animation's presentation timing.
            sample_ms = (duration - 1) * frame / (FRAMES_PER_EXPERIMENT - 1)
            source_index = next(i for i, end in enumerate(ends) if end > sample_ms)
            selected.append(source_index)
            packaged = create_frame(originals[source_index], experiment, frame)
            output_frames.append(packaged)
        source_report.append({'title': title, 'source': filename,
                              'source_duration_ms': duration,
                              'sampled_frames': selected})

    # A stable palette for each experiment preserves its original chart colors.
    # Full-resolution samples matter: thumbnail-only palettes can average thin
    # colored coefficient paths into gray. No dithering or per-frame palettes.
    quantized = []
    for experiment in range(len(EXPERIMENTS)):
        experiment_frames = output_frames[
            experiment * FRAMES_PER_EXPERIMENT:(experiment + 1) * FRAMES_PER_EXPERIMENT]
        palette_sheet = Image.new('RGB', (WIDTH * 5, HEIGHT * 4))
        for index, frame in enumerate(experiment_frames):
            palette_sheet.paste(frame, ((index % 5) * WIDTH, (index // 5) * HEIGHT))
        palette = palette_sheet.quantize(colors=256, method=Image.Quantize.MEDIANCUT,
                                        dither=Image.Dither.NONE)
        quantized.extend(frame.quantize(palette=palette, dither=Image.Dither.NONE)
                         for frame in experiment_frames)
    quantized[0].save(OUTPUT, save_all=True, append_images=quantized[1:],
                      duration=FRAME_MS, loop=0, optimize=True, disposal=1)

    PREVIEW.parent.mkdir(exist_ok=True)
    sheet = Image.new('RGB', (WIDTH * 3, HEIGHT * 4), '#e7ecf2')
    with Image.open(OUTPUT) as encoded:
        for index in range(len(EXPERIMENTS)):
            encoded.seek(index * FRAMES_PER_EXPERIMENT + FRAMES_PER_EXPERIMENT // 2)
            sheet.paste(encoded.convert('RGB'), ((index % 3) * WIDTH, (index // 3) * HEIGHT))
    sheet.save(PREVIEW)

    with Image.open(OUTPUT) as result:
        durations = []
        for index in range(result.n_frames):
            result.seek(index)
            durations.append(result.info['duration'])
        assert result.n_frames == 11 * FRAMES_PER_EXPERIMENT, result.n_frames
        assert all(duration == FRAME_MS for duration in durations), durations
        assert result.info.get('loop') == 0
        assert result.size == (WIDTH, HEIGHT)
        assert sum(durations) == 55000
        for experiment in range(11):
            section = durations[experiment * 20:(experiment + 1) * 20]
            assert sum(section) == 5000
    report = {'output': str(OUTPUT), 'bytes': OUTPUT.stat().st_size,
              'sha256': hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
              'frames': len(durations), 'frame_duration_ms': FRAME_MS,
              'each_experiment_ms': 5000, 'total_duration_ms': sum(durations),
              'loop': 0, 'dimensions': [WIDTH, HEIGHT], 'sources': source_report,
              'contact_sheet': str(PREVIEW)}
    report_path = PREVIEW.with_suffix('.json')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'sources'}, indent=2))


if __name__ == '__main__':
    main()
