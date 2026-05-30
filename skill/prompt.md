# Demo Reel — agent prompt

Build a narrated product demo video pipeline for `{PROJECT_NAME}`.

## Goal

Produce `dist/{project_slug}_demo.mp4` (~60–120s) with TTS narration, smooth scroll/zoom animation, a live interaction beat, and one-command rebuild.

## Architecture (required)

Do NOT use Playwright `record_video_dir` as primary capture — it freezes on long waits.

```
narration.txt → TTS → duration
       ↓
/demo?record=1&duration=SECONDS
       ↓
window.__demoRecorder.seek(t) each frame @ 24fps
       ↓
ffmpeg → MP4
```

Use **demo-reel** CLI:

```bash
demo-reel init
demo-reel build --config demo-reel.yaml --validate
```

## Demo page requirements

- `#demo-viewport` with `translateY()` + `scale()` transforms
- `.record-focus` on active section; `.record-active` on list items / metrics
- Prefetch live API in record mode; typewriter JSON via `reveal` fraction 0–1
- Hide non-video chrome in record mode

## Quality checklist

- [ ] 4 sample frames at 0/33/66/100% have different hashes
- [ ] MP4 duration matches narration ±1s
- [ ] No >5s static hold at one scroll position
- [ ] Interactive `/demo` works without `?record=1`

## Config (`demo-reel.yaml`)

```yaml
server:
  command: ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "{port}"]
  health_path: /healthz
  demo_path: /demo?record=1&duration={duration}
narration:
  file: narration.txt
  tts: edge
output:
  dir: dist
  filename: demo.mp4
```

See https://github.com/mdscaff/demo-reel for examples and CI templates.
