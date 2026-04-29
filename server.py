from __future__ import annotations

from pathlib import Path

from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from model import config_from_mapping, run_simulation


APP_DIR = Path(__file__).parent

app = FastAPI(title="Traffic Congestion Agent-Based Model")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["null"],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (APP_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "project": "traffic-congestion-abm"}


@app.post("/simulate")
def simulate(payload: dict | None = Body(default=None)) -> dict:
    config = config_from_mapping(payload)
    return run_simulation(config)
