from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

from demo_reel import __version__
from demo_reel.build import build_demo
from demo_reel.config import load_config
from demo_reel.doctor import run_doctor
from demo_reel.validate import validate_not_static

PKG_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = PKG_ROOT / "templates"
SKILL_DIR = PKG_ROOT / "skill"


def _ensure_path() -> None:
    if sys.platform == "darwin":
        brew_bin = Path("/opt/homebrew/bin")
        if brew_bin.is_dir():
            os.environ["PATH"] = str(brew_bin) + os.pathsep + os.environ.get("PATH", "")


def cmd_build(args: argparse.Namespace) -> int:
    config_path = Path(args.config).resolve()
    config = load_config(config_path)
    if args.tts:
        config.narration.tts = args.tts
    if args.port:
        config.server.port = args.port
    if args.keep_frames:
        config.output.keep_frames = True
    build_demo(config)
    if args.validate:
        ok, message = validate_not_static(config.output_mp4())
        print(f"[demo-reel] validate: {message}")
        return 0 if ok else 1
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    video = Path(args.video).resolve()
    if not video.is_file():
        print(f"Missing video: {video}", file=sys.stderr)
        return 1
    ok, message = validate_not_static(video)
    print(message)
    return 0 if ok else 1


def cmd_init(args: argparse.Namespace) -> int:
    target = Path(args.directory or ".").resolve()
    target.mkdir(parents=True, exist_ok=True)

    config_dest = target / "demo-reel.yaml"
    if config_dest.exists() and not args.force:
        print(f"Already exists: {config_dest} (use --force)", file=sys.stderr)
        return 1

    shutil.copy(TEMPLATES / "demo-reel.yaml", config_dest)
    shutil.copy(TEMPLATES / "narration.txt", target / "narration.txt")

    skill_dest = target / ".cursor" / "skills" / "demo-reel"
    if SKILL_DIR.is_dir():
        skill_dest.parent.mkdir(parents=True, exist_ok=True)
        if skill_dest.exists():
            shutil.rmtree(skill_dest)
        shutil.copytree(SKILL_DIR, skill_dest)

    print(f"Initialized demo-reel in {target}")
    print("  demo-reel.yaml")
    print("  narration.txt")
    print("  .cursor/skills/demo-reel/SKILL.md")
    print("\nNext: implement your /demo page with __demoRecorder.seek(t), then:")
    print("  demo-reel build --config demo-reel.yaml")
    return 0


def cmd_doctor(_: argparse.Namespace) -> int:
    return run_doctor()


def main() -> int:
    _ensure_path()
    parser = argparse.ArgumentParser(prog="demo-reel", description="Narrated product demo videos")
    parser.add_argument("--version", action="version", version=f"demo-reel {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="Generate narrated demo MP4 from config")
    build.add_argument("--config", "-c", default="demo-reel.yaml", help="Path to config YAML")
    build.add_argument("--tts", choices=("edge", "elevenlabs"), help="Override TTS backend")
    build.add_argument("--port", type=int, help="Override server port")
    build.add_argument("--keep-frames", action="store_true", help="Keep PNG frames after encode")
    build.add_argument("--validate", action="store_true", help="Run static-frame check after build")
    build.set_defaults(func=cmd_build)

    validate = sub.add_parser("validate", help="Check MP4 is not a static image")
    validate.add_argument("video", help="Path to MP4")
    validate.set_defaults(func=cmd_validate)

    init = sub.add_parser("init", help="Scaffold demo-reel.yaml and narration stub")
    init.add_argument("directory", nargs="?", help="Target directory (default: cwd)")
    init.add_argument("--force", action="store_true", help="Overwrite existing config")
    init.set_defaults(func=cmd_init)

    doctor = sub.add_parser("doctor", help="Check ffmpeg, playwright, edge-tts")
    doctor.set_defaults(func=cmd_doctor)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
