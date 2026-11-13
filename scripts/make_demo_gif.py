"""Build docs/assets/review-demo.gif: four frames of the published static replay.

    uv run --with pillow python scripts/make_demo_gif.py

Frames (from https://professor3333.github.io/LocalityLens/, the replay of the 50 audit records):
the review queue; a ready record (label with its spans, interpretation, map with the region);
a record that selection-2 holds (label and map); and the question that holds it. Screenshots
come from Playwright's chrome-headless-shell (CHROME, or the newest one in the Playwright
cache); map tiles load from USGS, so the network is needed.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

BASE = "https://professor3333.github.io/LocalityLens"
OUT = Path("docs/assets/review-demo.gif")
WIDTH, HEIGHT = 1280, 860  # every frame is cropped to this, then scaled to 960 wide
# (page, window height, crop top): crop boxes chosen on the replay as built at ff53126
FRAMES = [
    ("index.html", 1400, 0),  # queue, with the replay banner
    ("records/gbif-2573344610.html", 1400, 230),  # ready: Flagstaff Mountain, 2,039 m region
    ("records/gbif-2573441754.html", 1400, 230),  # held by selection-2: Paonia offset
    ("records/gbif-2573441754.html", 2400, 700),  # ... and the question that holds it
]
SECONDS = 3.0


def _chrome() -> str:
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    cache = Path.home() / "Library/Caches/ms-playwright"
    if not cache.is_dir():
        cache = Path.home() / ".cache/ms-playwright"
    found = sorted(
        cache.glob("chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell")
    )
    if not found:
        sys.exit(
            "no chrome-headless-shell: run `uv run playwright install chromium-headless-shell`"
        )
    return str(found[-1])


def main() -> None:
    chrome = _chrome()
    frames = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, (page, height, top) in enumerate(FRAMES):
            shot = Path(tmp) / f"{i}.png"
            subprocess.run(
                [chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
                 f"--window-size={WIDTH},{height}", "--virtual-time-budget=8000",
                 f"--screenshot={shot}", f"{BASE}/{page}"],
                check=True, capture_output=True, timeout=120,
            )  # fmt: skip
            image = Image.open(shot).convert("RGB").crop((0, top, WIDTH, top + HEIGHT))
            frames.append(image.resize((960, round(HEIGHT * 960 / WIDTH)), Image.LANCZOS))
    palette = [f.quantize(colors=128, method=Image.Quantize.MEDIANCUT) for f in frames]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    palette[0].save(OUT, save_all=True, append_images=palette[1:],
                    duration=int(SECONDS * 1000), loop=0, optimize=True)  # fmt: skip
    print(f"{OUT}: {len(frames)} frames, {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
