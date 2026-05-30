from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"

app = FastAPI(title="Demo Reel Example")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/demo")
def demo() -> FileResponse:
    return FileResponse(STATIC / "demo.html", media_type="text/html")


@app.post("/api/hello")
def hello(payload: dict) -> dict:
    name = payload.get("name", "world")
    return {
        "message": f"Hello, {name}!",
        "accepted": True,
        "telemetry": {"latency_ms": 12, "cache_hit": False, "version": "0.1.0"},
    }
