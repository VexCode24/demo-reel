# Demo Reel

**Narrated MP4 product demo videos from live web pages** — synced zoom, scroll, highlights, and a real API beat. One CLI command. CI-ready on every release.

Born from the [Roubaix](https://github.com/mdscaff/roubaix) demo pipeline. Extracted as a reusable toolkit and agent skill.

## Why not screen recording?

| Approach | Problem |
|----------|---------|
| Manual Loom / QuickTime | Drifts from shipped product; not reproducible |
| Playwright `record_video_dir` | Long idle waits → video looks **frozen** |
| Slides | No live API proof |

Demo Reel uses **seek-synced frame capture**: every frame calls `window.__demoRecorder.seek(t)` so pan, zoom, and highlights match the narration.

## Quick start

```bash
git clone https://github.com/mdscaff/demo-reel.git
cd demo-reel
pip install -e ".[capture]"
python -m playwright install chromium
demo-reel doctor

# Build the included example (~60s, Edge TTS, no API key)
demo-reel build --config demo-reel.yaml --validate
# → dist/demo_reel_example.mp4
```

## Add to your project

```bash
pip install "demo-reel[capture] @ git+https://github.com/mdscaff/demo-reel.git"
demo-reel init
# Edit narration.txt, implement /demo with __demoRecorder.seek(t)
demo-reel build --config demo-reel.yaml --validate
```

### Demo page contract

```
GET /demo?record=1&duration=90
```

```javascript
window.__demoRecorder = {
  seek(t) { /* translateY + scale, section focus, API typewriter */ }
};
window.__demoRecorderReady = true;
```

See `examples/minimal-fastapi/static/demo.html` for a complete reference.

## Configuration (`demo-reel.yaml`)

```yaml
server:
  command: ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "{port}"]
  health_path: /healthz
  demo_path: /demo?record=1&duration={duration}
  cwd: .                          # optional working directory

narration:
  file: narration.txt
  tts: edge                       # edge (free) | elevenlabs

capture:
  fps: 24

output:
  dir: dist
  filename: demo.mp4
```

## CI/CD — demo video on every release

Add to your repo (copy from `examples/github-workflow-release-demo.yml`):

```yaml
on:
  release:
    types: [published]

jobs:
  demo-video:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: mdscaff/demo-reel/.github/actions/build@main
        with:
          config: demo-reel.yaml
          tts: edge
          validate: "true"
      - uses: softprops/action-gh-release@v2
        with:
          files: dist/*.mp4
```

Every major release ships with an **overview video** attached — no manual recording.

## Agent skill (Cursor / Claude Code)

Install the skill for coding agents:

```bash
git clone https://github.com/mdscaff/demo-reel.git ~/.cursor/skills/demo-reel
# skill lives at ~/.cursor/skills/demo-reel/skill/SKILL.md
```

Or run `demo-reel init` in your project — it copies the skill to `.cursor/skills/demo-reel/`.

Trigger: *"Build a narrated demo video for this release"* → agent follows `skill/SKILL.md`.

## CLI

| Command | Description |
|---------|-------------|
| `demo-reel build` | Generate MP4 from config |
| `demo-reel validate` | Ensure video is not a static image |
| `demo-reel init` | Scaffold config + narration + skill |
| `demo-reel doctor` | Check ffmpeg, playwright, edge-tts |

```bash
demo-reel build --config demo-reel.yaml --tts elevenlabs --validate
```

**ElevenLabs:** set `ELEVENLABS_API_KEY` and optional `ELEVENLABS_VOICE_ID`.

## Docs

- [Architecture](docs/architecture.md)
- [Keyframe authoring](docs/keyframe-authoring.md)
- [Agent prompt](skill/prompt.md)

## License

MIT
