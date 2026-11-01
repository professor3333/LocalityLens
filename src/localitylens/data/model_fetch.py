"""Download the pinned GGUF from the release manifest and verify size and SHA-256.

The file lands in ``models/`` (gitignored). The download goes to a temporary name and is
renamed only after the checksum matches, so a partial or altered file is never used.
"""

from __future__ import annotations

import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Final

from localitylens.data.manifest import ChecksumMismatchError, sha256_file
from localitylens.release import ModelPin

_USER_AGENT: Final = "LocalityLens-ingest/0.1 (+https://github.com/professor3333/LocalityLens)"
_CHUNK: Final = 8 << 20


def verify_model(path: Path, pin: ModelPin) -> None:
    if not path.is_file():
        raise ChecksumMismatchError(f"{path} is missing; run `localitylens model fetch`")
    if path.stat().st_size != pin.gguf_size_bytes:
        raise ChecksumMismatchError(f"{path} size differs from the release manifest")
    if (actual := sha256_file(path)) != pin.gguf_sha256:
        raise ChecksumMismatchError(f"{path} sha256 {actual} != pinned {pin.gguf_sha256}")


def _download(url: str, dest: Path, progress: Callable[[int], None]) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as resp, dest.open("wb") as out:
        done = 0
        while chunk := resp.read(_CHUNK):
            out.write(chunk)
            done += len(chunk)
            progress(done)


def fetch_model(
    models_dir: Path,
    pin: ModelPin,
    *,
    download: Callable[[str, Path, Callable[[int], None]], None] = _download,
    progress: Callable[[int], None] = lambda _done: None,
) -> Path:
    final = models_dir / pin.gguf_file
    if final.exists():
        verify_model(final, pin)  # raises rather than silently replacing a different file
        return final
    models_dir.mkdir(parents=True, exist_ok=True)
    partial = models_dir / f".{pin.gguf_file}.partial"
    try:
        download(pin.url, partial, progress)
        verify_model(partial, pin)
        partial.rename(final)
    finally:
        if partial.exists():
            partial.unlink()
    return final


def copy_progress(total: int) -> Callable[[int], None]:
    step = max(total // 20, 1)
    last = [0]

    def report(done: int) -> None:
        if done - last[0] >= step or done == total:
            last[0] = done
            print(f"  {done / total:6.1%}  {done:>14,} / {total:,} bytes", flush=True)

    return report
