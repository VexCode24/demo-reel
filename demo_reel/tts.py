from __future__ import annotations

import asyncio
import os
from pathlib import Path

import httpx

from demo_reel.config import NarrationConfig


async def write_edge_tts(text: str, out_mp3: Path, voice: str) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text, voice=voice)
    await communicate.save(str(out_mp3))


def write_elevenlabs_tts(text: str, out_mp3: Path) -> None:
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise RuntimeError("ELEVENLABS_API_KEY is not set")
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM").strip()
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = {"text": text, "model_id": "eleven_multilingual_v2"}
    headers = {
        "xi-api-key": key,
        "accept": "audio/mpeg",
        "content-type": "application/json",
    }
    with httpx.Client(timeout=120.0) as client:
        response = client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        out_mp3.write_bytes(response.content)


def synthesize_narration(text: str, out_mp3: Path, config: NarrationConfig) -> None:
    if config.tts == "elevenlabs":
        write_elevenlabs_tts(text, out_mp3)
        return
    asyncio.run(write_edge_tts(text, out_mp3, config.edge_voice))
