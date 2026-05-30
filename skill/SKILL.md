---
name: demo-reel
description: >-
  Builds narrated MP4 product demo videos from a web page using seek-synced
  Playwright frame capture, TTS narration, and ffmpeg. Use when the user asks
  for a demo video, product walkthrough, narrated screencast, release overview
  video, or CEO demo. Supports CI/CD on release tags.
---

# Demo Reel

Generate **narrated MP4 product demos** from a live web page — not static screenshots.

## When to use

- User wants a demo video, release overview video, or narrated walkthrough
- Adding demo video generation to CI/CD on release
- Rebuilding a video after copy or UI changes

## Quick start

```bash
pip install "demo-reel[capture]"   # or: pip install git+https://github.com/mdscaff/demo-reel.git#egg=demo-reel[capture]
python -m playwright install chromium
demo-reel doctor
demo-reel init
demo-reel build --config demo-reel.yaml --validate
```

## Required demo page contract

Record mode: `/demo?record=1&duration=SECONDS`

```javascript
window.__demoRecorder = { seek(t) { /* pan, zoom, highlights, API reveal */ } };
window.__demoRecorderReady = true;
```

**Do not** use Playwright `record_video_dir` as the primary capture method.

## Pipeline

```
narration.txt → TTS → ffprobe duration
                 ↓
    demo page seek(t) @ 24fps screenshots
                 ↓
         ffmpeg encode + mux → demo.mp4
```

## Agent workflow

1. Run `demo-reel init` or read existing `demo-reel.yaml`
2. Write `narration.txt` (~150–250 words): hook → problems → outcomes → live beat → close
3. Implement `/demo` with `#demo-viewport`, keyframe timeline, `__demoRecorder.seek(t)`
4. Map keyframe times to narration beats (see [prompt.md](prompt.md))
5. Run `demo-reel build --config demo-reel.yaml --validate`
6. For CI: add `.github/workflows/release-demo.yml` (see repo `examples/github-workflow-release-demo.yml`)

## Keyframe timing template

| Beat | Time fraction | Visual |
|------|---------------|--------|
| Hook | 0.00–0.10 | Zoom hero |
| Problems | 0.10–0.28 | Pan + highlight bullets |
| Outcomes | 0.28–0.44 | Metric pulses |
| Features | 0.44–0.56 | Section zoom |
| Live demo | 0.56–0.72 | CTA → API → typewriter JSON |
| Proof | 0.72–0.85 | Zoom result |
| Close | 0.85–1.00 | Zoom out |

## CI/CD (release video)

On `release` or tag push, use the GitHub Action:

```yaml
- uses: mdscaff/demo-reel/.github/actions/build@main
  with:
    config: demo-reel.yaml
    tts: edge
- uses: softprops/action-gh-release@v2
  with:
    files: dist/demo.mp4
```

## Reference

- Full agent prompt: [prompt.md](prompt.md)
- Example app: `examples/minimal-fastapi/`
- Architecture: [../docs/architecture.md](../docs/architecture.md)
