# Keyframe authoring

Define keyframes as `{ t, scroll, zoom, originY, focus, … }` where `t` is seconds from start.

## Rules

1. **Align to narration** — read narration aloud; place keyframes at phrase boundaries
2. **Keep moving** — no gap >3s without scroll, zoom, or highlight change
3. **Ease transitions** — use easeInOut between keyframes (see example `static/demo.html`)
4. **Live beat** — demo states: `idle` → `armed` → `calling` → `result` with `reveal` 0→1

## Section IDs

Use stable `id` attributes: `hero`, `problems`, `outcomes`, `live-demo`.

## Testing locally

Open `/demo?record=1&duration=60` and in DevTools:

```javascript
let t = 0;
setInterval(() => { window.__demoRecorder.seek(t); t += 0.5; }, 500);
```

## Validate

```bash
demo-reel build --validate
demo-reel validate dist/demo.mp4
```
