from __future__ import annotations

import shutil
import signal
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from demo_reel.config import DemoReelConfig


def wait_for_health(url: str, timeout_s: float = 60.0) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
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
    env = {**dict(**__import__("os").environ), **config.server.env}
    return subprocess.Popen(
        config.server_command(),
        cwd=str(cwd),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def stop_server(proc: subprocess.Popen) -> None:
    proc.send_signal(signal.SIGTERM)
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


def record_frames(config: DemoReelConfig, duration_s: float, demo_url: str) -> Path:
    from playwright.sync_api import sync_playwright

    frames_dir = config.frames_dir()
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True)

    fps = config.capture.fps
    total_frames = max(1, int(round(duration_s * fps)))

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

        for frame_idx in range(total_frames):
            t = frame_idx / fps
            page.evaluate("(t) => window.__demoRecorder.seek(t)", t)
            page.wait_for_timeout(16)
            page.screenshot(
                path=str(frames_dir / f"frame_{frame_idx:06d}.png"),
                type="png",
                animations="disabled",
            )

        context.close()
        browser.close()

    return frames_dir
