#!/usr/bin/env python3
"""Build eleven matching dark scientific cards and their 66-second showcase.

Each experiment has 24 frames at 250 ms: exactly six seconds. All cards use
the supplied Monte Carlo reference layout, without a second outer frame.
Run with --preview-only to inspect one representative frame per experiment.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image
from statistical_cards import (WIDTH, HEIGHT, FRAME_MS, FRAMES_PER_EXPERIMENT,
                               EXPERIMENTS, NAVY, render)

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
PREVIEW = ROOT / 'preview'
OUTPUT = ASSETS / 'experiments-showcase.gif'


def verify(path, experiments=1):
    durations = []
    with Image.open(path) as image:
        assert image.size == (WIDTH, HEIGHT)
        assert image.info.get('loop') == 0
        assert image.n_frames == FRAMES_PER_EXPERIMENT * experiments
        for i in range(image.n_frames):
            image.seek(i)
            durations.append(image.info['duration'])
    assert all(t == FRAME_MS for t in durations)
    sections = [sum(durations[i:i+FRAMES_PER_EXPERIMENT])
                for i in range(0, len(durations), FRAMES_PER_EXPERIMENT)]
    assert sections == [6000] * experiments
    data = path.read_bytes()
    return {'file': path.name, 'bytes': len(data), 'frames': len(durations),
            'dimensions': [WIDTH, HEIGHT], 'loop': 0,
            'each_experiment_ms': 6000, 'total_duration_ms': sum(durations),
            'sha256': hashlib.sha256(data).hexdigest(),
            'git_blob_sha': hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()}


def encode(frames):
    # A fixed, full-resolution palette for each experiment preserves thin curves.
    sheet = Image.new('RGB', (WIDTH * 6, HEIGHT * 4), NAVY)
    for k, frame in enumerate(frames):
        sheet.paste(frame, ((k % 6) * WIDTH, (k // 6) * HEIGHT))
    palette = sheet.quantize(colors=256, method=Image.Quantize.MEDIANCUT,
                             dither=Image.Dither.NONE)
    return [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]


def save(frames, path):
    frames[0].save(path, save_all=True, append_images=frames[1:],
                   duration=FRAME_MS, loop=0, optimize=True, disposal=1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preview-only', action='store_true')
    preview_only = parser.parse_args().preview_only
    PREVIEW.mkdir(exist_ok=True)
    ASSETS.mkdir(exist_ok=True)
    contact = Image.new('RGB', (WIDTH * 3, HEIGHT * 4), NAVY)
    all_frames, reports = [], []
    for index, (stem, title) in enumerate(EXPERIMENTS):
        if preview_only:
            frame = render(index, FRAMES_PER_EXPERIMENT // 2)
            contact.paste(frame, ((index % 3) * WIDTH, (index // 3) * HEIGHT))
            continue
        frames = [render(index, k) for k in range(FRAMES_PER_EXPERIMENT)]
        encoded = encode(frames)
        card_path = ASSETS / (stem + '.gif')
        save(encoded, card_path)
        reports.append(verify(card_path))
        all_frames.extend(encoded)
        contact.paste(encoded[FRAMES_PER_EXPERIMENT // 2].convert('RGB'),
                      ((index % 3) * WIDTH, (index // 3) * HEIGHT))
        sample = Image.new('RGB', (WIDTH * 3, HEIGHT), NAVY)
        for j, k in enumerate([0, FRAMES_PER_EXPERIMENT // 2, FRAMES_PER_EXPERIMENT - 1]):
            sample.paste(encoded[k].convert('RGB'), (j * WIDTH, 0))
        sample.save(PREVIEW / (stem + '-dark-review.png'))
        print(f'Validated {index+1}/11: {title} — 6 seconds', flush=True)
    contact.save(PREVIEW / 'experiments-showcase-contact-sheet.png')
    if preview_only:
        print('All eleven reference-style previews rendered without clipped card text.')
        return
    save(all_frames, OUTPUT)
    report = verify(OUTPUT, len(EXPERIMENTS))
    report['cards'] = reports
    report['style'] = 'Dark reference card: navy background, serif title, chart, three result boxes'
    (PREVIEW / 'experiments-showcase-contact-sheet.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'cards'}, indent=2))


if __name__ == '__main__':
    main()
