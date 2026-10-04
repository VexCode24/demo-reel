from __future__ import annotations

import subprocess
import sys
from shutil import which


def run_doctor() -> int:
    ok = True
    for binary in ("ffmpeg", "ffprobe"):
        if which(binary):
            print(f"✓ {binary} found")
        else:
            print(f"✗ {binary} missing — install ffmpeg")
            ok = False

    try:
        import playwright  # noqa: F401

        print("✓ playwright installed")
    except ImportError:
        print("✗ playwright missing — pip install 'demo-reel[capture]'")
        ok = False

    try:
        import edge_tts  # noqa: F401

        print("✓ edge-tts installed")
    except ImportError:
        print("✗ edge-tts missing — pip install 'demo-reel[capture]'")
        ok = False

    if which("playwright"):
        proc = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium", "--dry-run"],
            capture_output=True,
            check=False,
            text=True,
        )
        if proc.returncode == 0:
            print("✓ playwright CLI available")
        else:
            print("⚠ run: python -m playwright install chromium")
    else:
        print("⚠ run: python -m playwright install chromium")

    return 0 if ok else 1
