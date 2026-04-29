import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
from pydantic import BaseModel
import numpy as np

from preview import generate_preview

app = FastAPI()

# frontend_path = os.path.join(os.getcwd(), "docs-site", "build")
# if os.path.exists(os.path.join(frontend_path, "assets")):
#     app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

# @app.get("/")
# async def serve_index():
#     return FileResponse(os.path.join(frontend_path, "index.html"))

# @app.get("/{rest_of_path:path}")
# async def serve_everything_else(rest_of_path: str):
#     file_path = os.path.join(frontend_path, rest_of_path)
#     if os.path.isfile(file_path):
#         return FileResponse(file_path)
#     return FileResponse(os.path.join(frontend_path, "index.html"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://a-darcher.github.io",
        "https://alanadarcher.com",
        "https://www.alanadarcher.com",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
from pydantic import BaseModel
import numpy as np

from preview import generate_preview

app = FastAPI()

# frontend_path = os.path.join(os.getcwd(), "docs-site", "build")
# if os.path.exists(os.path.join(frontend_path, "assets")):
#     app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

# @app.get("/")
# async def serve_index():
#     return FileResponse(os.path.join(frontend_path, "index.html"))

# @app.get("/{rest_of_path:path}")
# async def serve_everything_else(rest_of_path: str):
#     file_path = os.path.join(frontend_path, rest_of_path)
#     if os.path.isfile(file_path):
#         return FileResponse(file_path)
#     return FileResponse(os.path.join(frontend_path, "index.html"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://a-darcher.github.io",
        "https://alanadarcher.com",
        "https://www.alanadarcher.com",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
class PreviewRequest(BaseModel):
    baseline_fr: float = 5.0
    response_fr: float = 20.0
    latency: float = 0.1
    duration: float = 0.2
    baseline_T: float = 1.0
    stimulus_T: float = 1.0
    dt: float = 0.001
    induce_refractory_period: bool = True
    seed: int = 42
    a: float | None = None
    b: float | None = None
    include_bursts: bool = False
    burst_rate_baseline: float = 1.0
    burst_rate_response: float = 2.0
    burst_rate_factor: float = 0.25
    burst_duration_lam: float = 20.0
    burst_alpha: float = 2.0
    burst_beta: float = 2.0
    burst_multiplier: float = 2.0
    n_trials: int = 100
    debug: bool = False

import traceback

@app.post("/preview")
def preview(req: PreviewRequest):
    try:
        return generate_preview(
            baseline_fr=req.baseline_fr,
            response_fr=req.response_fr,
            latency=req.latency,
            duration=req.duration,
            baseline_T=req.baseline_T,
            stimulus_T=req.stimulus_T,
            dt=req.dt,
            induce_refractory_period=req.induce_refractory_period,
            rng=np.random.default_rng(req.seed),
            a=req.a,
            b=req.b,
            include_bursts=req.include_bursts,
            burst_rate_baseline=req.burst_rate_baseline,
            burst_rate_response=req.burst_rate_response,
            burst_rate_factor=req.burst_rate_factor,
            burst_duration_lam=req.burst_duration_lam,
            burst_alpha=req.burst_alpha,
            burst_beta=req.burst_beta,
            burst_multiplier=req.burst_multiplier,
            n_trials=req.n_trials,
            debug=req.debug,
        )
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))
    
def validate_preview_request(req: PreviewRequest) -> list[str]:
    errors = []

    if req.n_trials < 1:
        errors.append("Number of trials must be at least 1.")

    if req.baseline_fr < 0:
        errors.append("Baseline firing rate must be non-negative.")

    if req.response_fr < 0:
        errors.append("Response firing rate must be non-negative.")

    if req.baseline_T <= 0:
        errors.append("Baseline window must be positive.")

    if req.stimulus_T <= 0:
        errors.append("Stimulus window must be positive.")

    if req.dt <= 0:
        errors.append("dt must be positive.")

    if req.latency < 0:
        errors.append("Latency must be non-negative.")

    if req.duration <= 0:
        errors.append("Duration must be positive.")

    if req.latency > req.stimulus_T:
        errors.append("Latency cannot exceed stimulus window.")

    if req.latency + req.duration > req.stimulus_T:
        errors.append("Latency + duration cannot exceed stimulus window.")

    if req.include_bursts:
        if req.burst_rate_baseline < 0:
            errors.append("Burst baseline rate must be non-negative.")

        if req.burst_rate_response < 0:
            errors.append("Burst response rate must be non-negative.")

        if req.burst_rate_factor < 0:
            errors.append("Burst rate factor must be non-negative.")

        if req.burst_duration_lam <= 0:
            errors.append("Burst duration λ must be positive.")

        if req.burst_multiplier <= 0:
            errors.append("Burst multiplier must be positive.")

    if req.a is not None and req.a <= 0:
        errors.append("Beta alpha must be positive.")

    if req.b is not None and req.b <= 0:
        errors.append("Beta beta must be positive.")

    return errors

class PreviewRequest(BaseModel):
    baseline_fr: float = 5.0
    response_fr: float = 20.0
    latency: float = 0.1
    duration: float = 0.2
    baseline_T: float = 1.0
    stimulus_T: float = 1.0
    dt: float = 0.001
    induce_refractory_period: bool = True
    seed: int = 42
    a: float | None = None
    b: float | None = None
    include_bursts: bool = False
    burst_rate_baseline: float = 1.0
    burst_rate_response: float = 2.0
    burst_rate_factor: float = 0.25
    burst_duration_lam: float = 20.0
    burst_alpha: float = 2.0
    burst_beta: float = 2.0
    burst_multiplier: float = 2.0
    n_trials: int = 100
    debug: bool = False

import traceback

@app.post("/preview")
def preview(req: PreviewRequest):
    errors = validate_preview_request(req)

    if errors:
        return {
            "ok": False,
            "image_base64": None,
            "stats": {},
            "warnings": errors,
        }

    try:
        return generate_preview(
            baseline_fr=req.baseline_fr,
            response_fr=req.response_fr,
            latency=req.latency,
            duration=req.duration,
            baseline_T=req.baseline_T,
            stimulus_T=req.stimulus_T,
            dt=req.dt,
            induce_refractory_period=req.induce_refractory_period,
            rng=np.random.default_rng(req.seed),
            a=req.a,
            b=req.b,
            include_bursts=req.include_bursts,
            burst_rate_baseline=req.burst_rate_baseline,
            burst_rate_response=req.burst_rate_response,
            burst_rate_factor=req.burst_rate_factor,
            burst_duration_lam=req.burst_duration_lam,
            burst_alpha=req.burst_alpha,
            burst_beta=req.burst_beta,
            burst_multiplier=req.burst_multiplier,
            n_trials=req.n_trials,
            debug=req.debug,
        )
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))
