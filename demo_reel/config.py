from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8899
    command: list[str] = Field(
        default_factory=lambda: [
            "uvicorn",
            "app:app",
            "--host",
            "127.0.0.1",
            "--port",
            "{port}",
        ]
    )
    health_path: str = "/healthz"
    demo_path: str = "/demo?record=1&duration={duration}"
    cwd: str | None = None
    env: dict[str, str] = Field(default_factory=dict)


class NarrationConfig(BaseModel):
    file: str = "narration.txt"
    tts: Literal["edge", "elevenlabs"] = "edge"
    edge_voice: str = "en-US-GuyNeural"


class CaptureConfig(BaseModel):
    fps: int = 24
    viewport_width: int = 1280
    viewport_height: int = 720


class OutputConfig(BaseModel):
    dir: str = "dist"
    filename: str = "demo.mp4"
    keep_frames: bool = False


class DemoReelConfig(BaseModel):
    project_name: str = "My Project"
    server: ServerConfig = Field(default_factory=ServerConfig)
    narration: NarrationConfig = Field(default_factory=NarrationConfig)
    capture: CaptureConfig = Field(default_factory=CaptureConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)

    @property
    def root(self) -> Path:
        return Path(self._root)  # type: ignore[attr-defined]

    def resolve_path(self, relative: str) -> Path:
        path = Path(relative)
        if path.is_absolute():
            return path
        return self.root / path

    def output_mp4(self) -> Path:
        return self.resolve_path(self.output.dir) / self.output.filename

    def narration_path(self) -> Path:
        return self.resolve_path(self.narration.file)

    def frames_dir(self) -> Path:
        return self.resolve_path(self.output.dir) / "frames"

    def raw_video_path(self) -> Path:
        return self.resolve_path(self.output.dir) / "demo_raw.mp4"

    def audio_path(self) -> Path:
        return self.resolve_path(self.output.dir) / "demo_narration.mp3"

    def demo_url(self, duration: float) -> str:
        path = self.server.demo_path.format(duration=f"{duration:.2f}", port=self.server.port)
        if path.startswith("http"):
            return path
        return f"http://{self.server.host}:{self.server.port}{path}"

    def health_url(self) -> str:
        path = self.server.health_path
        if path.startswith("http"):
            return path
        return f"http://{self.server.host}:{self.server.port}{path}"

    def server_command(self) -> list[str]:
        return [
            part.format(port=str(self.server.port), duration="{duration}")
            for part in self.server.command
        ]


def load_config(path: Path) -> DemoReelConfig:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    config = DemoReelConfig.model_validate(data)
    config._root = path.parent.resolve()  # type: ignore[attr-defined]
    return config
