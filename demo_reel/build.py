from __future__ import annotations

import shutil
from pathlib import Path

from demo_reel.capture import record_frames, start_server, stop_server, wait_for_health
from demo_reel.config import DemoReelConfig
from demo_reel.ffmpeg_util import (
    encode_frames,
    mux_video_audio,
    probe_duration_seconds,
    require_ffmpeg,
)
from demo_reel.tts import synthesize_narration


def build_demo(config: DemoReelConfig) -> Path:
    require_ffmpeg()

    narration_path = config.narration_path()
    if not narration_path.is_file():
        raise FileNotFoundError(f"Missing narration file: {narration_path}")

    text = narration_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError("Narration file is empty")

    output_dir = config.resolve_path(config.output.dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    audio_path = config.audio_path()
    print(f"[demo-reel] Generating narration ({config.narration.tts})…")
    synthesize_narration(text, audio_path, config.narration)

    duration = probe_duration_seconds(audio_path) or 55.0
    fps = config.capture.fps
    print(f"[demo-reel] Narration {duration:.1f}s → {int(duration * fps)} frames @ {fps} fps")

    demo_url = config.demo_url(duration)
    proc = start_server(config)
    try:
        wait_for_health(config.health_url(), proc=proc)
        print(f"[demo-reel] Recording {demo_url}")
        frames_dir = record_frames(config, duration_s=duration, demo_url=demo_url)
    finally:
        stop_server(proc)

    raw_video = config.raw_video_path()
    print("[demo-reel] Encoding silent video…")
    encode_frames(frames_dir, fps, raw_video)

    if not config.output.keep_frames:
        shutil.rmtree(frames_dir, ignore_errors=True)

    out_mp4 = config.output_mp4()
    print("[demo-reel] Muxing final MP4…")
    mux_video_audio(raw_video, audio_path, out_mp4)
    print(f"[demo-reel] Done: {out_mp4}")
    return out_mp4
