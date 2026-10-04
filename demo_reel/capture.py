from __future__ import annotations

import os
import shutil
import signal
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from demo_reel.config import DemoReelConfig


def wait_for_health(
    url: str, timeout_s: float = 60.0, proc: subprocess.Popen | None = None
) -> None:
    """Poll until the server answers 200 — failing fast if the process dies first."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if proc is not None and proc.poll() is not None:
            raise RuntimeError(
                f"Server process exited with code {proc.returncode} before becoming "
                f"healthy at {url} — check the server command, cwd, and port."
            )
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                if resp.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.25)
    raise RuntimeError(f"Server did not become healthy at {url}")


def start_server(config: DemoReelConfig) -> subprocess.Popen:
    if config.server.cwd:
        cwd = Path(config.server.cwd)
        if not cwd.is_absolute():
            cwd = config.root / cwd
    else:
        cwd = config.root
    env = {**os.environ, **config.server.env}
    return subprocess.Popen(
        config.server_command(),
        cwd=str(cwd),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        # Own process group: wrapper commands (npm run …, uv run …) spawn the real
        # server as a child, and signalling only the wrapper orphans it — leaving
        # the port bound for every subsequent build.
        start_new_session=True,
    )


def stop_server(proc: subprocess.Popen) -> None:
    """Terminate the server's whole process group (wrapper + real server)."""

    def _signal_group(sig: signal.Signals) -> None:
        try:
            os.killpg(os.getpgid(proc.pid), sig)
        except (ProcessLookupError, PermissionError):
            proc.send_signal(sig)

    _signal_group(signal.SIGTERM)
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        _signal_group(signal.SIGKILL)
        proc.wait(timeout=5)


def record_frames(config: DemoReelConfig, duration_s: float, demo_url: str) -> Path:
    from playwright.sync_api import sync_playwright

    frames_dir = config.frames_dir()
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True)

    fps = config.capture.fps
    total_frames = max(1, round(duration_s * fps))

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={
                "width": config.capture.viewport_width,
                "height": config.capture.viewport_height,
            }
        )
        page = context.new_page()
        page.set_default_timeout(120_000)
        page.goto(demo_url, wait_until="domcontentloaded")
        page.wait_for_function("window.__demoRecorderReady === true")

        settle_ms = config.capture.settle_ms
        for frame_idx in range(total_frames):
            t = frame_idx / fps
            page.evaluate("(t) => window.__demoRecorder.seek(t)", t)
            page.wait_for_timeout(settle_ms)
            page.screenshot(
                path=str(frames_dir / f"frame_{frame_idx:06d}.png"),
                type="png",
                animations="disabled",
            )

        context.close()
        browser.close()

    return frames_dir
