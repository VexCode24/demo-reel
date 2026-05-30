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
pip install "demo-reel[capture] @ git+https://github.com/mdscaff/demo-reel.git@v0.1.0"
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

## Agent workflow

1. Run `demo-reel init` or read existing `demo-reel.yaml`
2. Write `narration.txt` (~150–250 words)
3. Implement `/demo` with `#demo-viewport`, keyframe timeline, `__demoRecorder.seek(t)`
4. Run `demo-reel build --config demo-reel.yaml --validate`
5. For CI: copy `examples/github-workflow-release-demo.yml`

## CI/CD (release video)

```yaml
- uses: mdscaff/demo-reel/.github/actions/build@v0.1.0
  with:
    config: demo-reel.yaml
    tts: edge
- uses: softprops/action-gh-release@v2
  with:
    files: dist/*.mp4
```

## Reference

- Full agent prompt: [skill/prompt.md](skill/prompt.md)
- Example app: [examples/minimal-fastapi/](examples/minimal-fastapi/)
- Docs: [docs/architecture.md](docs/architecture.md)
