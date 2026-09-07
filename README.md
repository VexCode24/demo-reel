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

## Pull request diagrams (PR Lens)

Every pull request against this repo gets drawn as animated **architecture** and **data-flow** diagrams by [PR Lens](https://github.com/coldteadotai/pr-lens), posted as one comment that is redrawn on each push. This is the pipeline itself, drawn the same way:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/diagrams/pipeline.dark.svg">
  <img alt="Demo Reel architecture: the CLI modules, the two endpoints your app must serve, and ffmpeg, Chromium and TTS on the far side" src="docs/diagrams/pipeline.light.svg">
</picture>

Three ways it runs here:

| Mode | What it needs | Where |
|------|---------------|-------|
| GitHub Action on every PR | a `GEMINI_API_KEY` repository secret (skips cleanly without it) | `.github/workflows/pr-lens.yml` |
| Coding agent (Claude Code, Cursor, …) | nothing — the agent writes the graph itself | `.claude/skills/pr-lens/` · or `npx skills add coldteadotai/pr-lens` |
| Locally, before the PR exists | `npx @coldtea/pr-lens-cli render <graph.json>` | `docs/diagrams/*.graph.json` |

Corrections (renames, lane pins, excluded paths) live in `.github/pr-lens.yml` — edit that, never a generated SVG. To redraw the pipeline map after a change:

```bash
npx @coldtea/pr-lens-cli@latest validate docs/diagrams/pipeline.graph.json
npx @coldtea/pr-lens-cli@latest render docs/diagrams/pipeline.graph.json --out .pr-lens
# then copy the pipeline-*.svg / build-run-view-*.svg pair into docs/diagrams/ under their stable names
```

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

- [Architecture](docs/architecture.md) — with the [PR Lens pipeline map](docs/diagrams/)
- [Keyframe authoring](docs/keyframe-authoring.md)
- [Agent prompt](skill/prompt.md)

## License

MIT
