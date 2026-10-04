from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from demo_reel.ffmpeg_util import probe_duration_seconds


def _frame_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def extract_sample_frames(video: Path, out_dir: Path, count: int = 4) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    duration = probe_duration_seconds(video) or 1.0
    paths: list[Path] = []
    fractions = [0.05, 0.35, 0.65, 0.92] if count == 4 else [i / max(count - 1, 1) for i in range(count)]
    for i, frac in enumerate(fractions[:count]):
        t = max(0.0, min(duration - 0.05, duration * frac))
        out = out_dir / f"sample_{i:02d}.png"
        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(t),
            "-i",
            str(video),
            "-frames:v",
            "1",
            str(out),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode == 0 and out.is_file():
            paths.append(out)
    return paths


def validate_not_static(video: Path) -> tuple[bool, str]:
    tmp = video.parent / ".validate_frames"
    try:
        frames = extract_sample_frames(video, tmp)
        if len(frames) < 2:
            return False, f"Could not extract enough sample frames (got {len(frames)})"
        hashes = {_frame_hash(p) for p in frames}
        if len(hashes) == 1:
            return False, "Video appears static — all sample frames identical"
        return True, f"OK — {len(hashes)} distinct frames across {len(frames)} samples"
    finally:
        import shutil

        shutil.rmtree(tmp, ignore_errors=True)
