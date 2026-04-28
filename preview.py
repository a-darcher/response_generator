import base64
import io
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from src.response_generator.generators import PoissonSpikeGenerator


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
    debug: bool,
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
        debug=debug,
    )

    trial_activity = [trial - baseline_T for trial in generator.generate(n_trials)]

    fig, axes = plt.subplots(2, 1, figsize=(8, 10), 
  
                            height_ratios=[2, 1])

    # raster asset
    ax = axes[0]
    ax.eventplot(trial_activity,)
    ax.vlines(0, ymin=-0.5, ymax=n_trials - 0.5, color="darkgoldenrod", linestyle="--", label="Stimulus onset")
    ax.set_title("")
    ax.set_xlabel("Time [s]\nsimulated stimulus onset at t = 0")
    ax.set_ylabel("Trials")

    ax.set_yticks([])

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # rate function asset
    ax = axes[1]
    x = np.linspace(-baseline_T, stimulus_T, int((baseline_T + stimulus_T) / dt))
    ax.plot(x, generator.r_t)
    ax.hlines(y=baseline_fr, xmin=-baseline_T, xmax=stimulus_T, color="olive", linestyle="--", alpha=0.5, label="Baseline firing rate")
    ax.vlines(0, ymin=baseline_fr, ymax=response_fr, color="darkgoldenrod", linestyle="--", label="Stimulus onset")

    ax.legend(frameon=False)

    ax.set_xlabel("Time [s]\nsimulated stimulus onset at t = 0")
    ax.set_ylabel("Rate Function [Hz]")

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    


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