from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np

from .preview import generate_preview

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://a-darcher.github.io",
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