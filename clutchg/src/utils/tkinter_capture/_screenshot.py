"""Screenshot helper — wraps capture + decode + save."""

from __future__ import annotations

import base64
from pathlib import Path


def save_screenshot(
    capture_fn,
    filepath: str | Path,
    max_dim: int = 1600,
    quality: int = 90,
) -> int:
    """Capture screenshot via RemoteBridge and save to file.

    Args:
        capture_fn: callable that returns base64-encoded screenshot string
                    (e.g., bridge.capture_screenshot)
        filepath: where to save the JPEG
        max_dim: max dimension for resizing
        quality: JPEG quality 1-100

    Returns:
        File size in bytes
    """
    b64_str = capture_fn(max_dimension=max_dim, quality=quality)
    if isinstance(b64_str, bytes):
        b64_str = b64_str.decode("utf-8")
    raw_jpeg = base64.b64decode(b64_str)
    path = Path(filepath)
    path.write_bytes(raw_jpeg)
    return path.stat().st_size
