import base64
import io
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from response_generator.generators import PoissonSpikeGenerator


def fig_to_base64_png(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


def generate_preview(
    baseline_fr: float,
    response_fr: float,
    latency: float,
    duration: float,
    baseline_T: float,
    stimulus_T: float,
    dt: float,
    induce_refractory_period: bool,
    rng: Any,
    a: float,
    b: float,
    include_bursts: bool,
    burst_rate_baseline: float,
    burst_rate_factor: float,
    burst_rate_response: float,
    burst_duration_lam: float,
    burst_alpha: float,
    burst_beta: float,
    burst_multiplier: float,
    n_trials: int,
) -> dict[str, Any]:
    """
    Run the real spike generator and return a JSON-safe preview.
    """

    if a is None:
        a = 1.0
    if b is None:
        b = 1.0

    generator = PoissonSpikeGenerator(
        baseline_fr=baseline_fr,
        response_fr=response_fr,
        latency=latency,
        duration=duration,
        baseline_T=baseline_T,
        stimulus_T=stimulus_T,
        dt=dt,
        induce_refractory_period=induce_refractory_period,
        rng=rng,
        a=a,
        b=b,
        include_bursts=include_bursts,
        burst_rate_baseline=burst_rate_baseline,
        burst_rate_factor= burst_rate_factor,
        burst_rate_response=burst_rate_response,
        burst_duration_lam=burst_duration_lam,
        burst_alpha=burst_alpha,
        burst_beta=burst_beta,
        burst_multiplier=burst_multiplier,
    )

    trial_activity = generator.generate(n_trials)


    fig, ax = plt.subplots(figsize=(7, 4))

    ax.eventplot(trial_activity,)
    ax.set_title("Generated Trial Activity")
    ax.set_xlabel("Time bin")
    ax.set_ylabel("Trial")

    image_base64 = fig_to_base64_png(fig)

    stats = {
        "n_trials": n_trials,
        "baseline_fr": baseline_fr,
        "response_fr": response_fr,
        "latency": latency,
        "duration": duration,
        "baseline_T": baseline_T,
        "stimulus_T": stimulus_T,
        "dt": dt,
        "include_bursts": include_bursts,
    }

    warnings: list[str] = []

    return {
        "ok": True,
        "image_base64": image_base64,
        "stats": stats,
        "warnings": warnings,
    }