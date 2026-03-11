import base64
import io
from typing import Any, List

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from response_generator.generators import PoissonSpikeGenerator


def fig_to_base64_png(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


def make_preview_figure(
    n_trials: int,
    baseline_fr: float,
    response_fr: float,
    duration: float,
    latency: float,
    a: float | None,
    b: float | None,
    baseline_T: float,
    stimulus_T: float,
    dt: float,
    induce_refractory_period: bool,
    generator: PoissonSpikeGenerator,
    trial_activity: List[np.ndarray],
) -> plt.Figure:
    fig, axes = plt.subplot_mosaic(
        [
            ["raster", "isi"],
            ["raster", "text"],
            ["r_t", "text"],
        ],
        empty_sentinel="empty",
        width_ratios=[2, 1],
        height_ratios=[1, 1, 0.4],
        figsize=(6, 4),
        layout="constrained",
    )

    ax = axes["raster"]
    ax.eventplot(trial_activity)
    ymin, ymax = ax.get_ylim()
    ax.vlines(0, ymin, ymax, colors="tab:orange")
    ax.set_xlim(-1 * baseline_T, stimulus_T)
    ax.set_xticklabels([])
    ax.set_yticks([])
    sns.despine(left=True, ax=ax)

    ax = axes["isi"]
    try:
        isis = np.concatenate([np.diff(t) for t in trial_activity if len(t) > 1])
        if len(isis) == 0:
            isis = np.zeros(1)
    except ValueError:
        isis = np.zeros(1)

    ax.hist(isis, bins=20)
    sns.despine(ax=ax)
    ax.set_xlabel("ISI [s]")
    ax.set_ylabel("count")

    ax = axes["r_t"]
    ax.plot(generator.r_t)
    ax.text(
        0.1, 1,
        "r(t)",
        transform=ax.transAxes,
        ha="left",
        va="top",
    )
    ax.set_xlabel("time [ms]")
    ax.set_ylabel("fr [Hz]")
    sns.despine(ax=ax)

    ax = axes["text"]
    ax.set_in_layout(False)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_anchor("NW")

    if a is not None and b is not None:
        s = (
            f"{n_trials} trials\n\n"
            f"params [time in sec]:\n"
            f"baseline FR:       {round(baseline_fr, 3)} Hz\n"
            f"response FR, peak: {round(response_fr, 3)} Hz\n"
            f"latency:           {round(latency, 3)}\n"
            f"duration:          {round(duration, 3)} s\n"
            f"baseline_T:        {baseline_T} s\n"
            f"stimulus_T:        {stimulus_T} s\n"
            f"dt:                {dt} s\n"
            f"induce_refractory: {induce_refractory_period}\n"
            f"beta({round(a, 3)}, {round(b, 3)})\n"
            f"burst rates - b: {round(generator.burst_rate_baseline, 3)}  "
            f"r: {round(generator.burst_rate_response, 3)}\n"
            f"avg. burst duration: {generator.burst_duration_lam} ms\n"
        )
    else:
        s = (
            f"{n_trials} trials\n\n"
            f"params [time in sec]:\n"
            f"baseline FR:       {round(baseline_fr, 3)} Hz\n"
            f"response FR, peak: {round(response_fr, 3)} Hz\n"
            f"latency:           {round(latency, 3)}\n"
            f"duration:          {round(duration, 3)} s\n"
            f"baseline_T:        {baseline_T} s\n"
            f"stimulus_T:        {stimulus_T} s\n"
            f"dt:                {dt} s\n"
            f"induce_refractory: {induce_refractory_period}\n"
            f"burst rates - b: {round(generator.burst_rate_baseline, 3)}  "
            f"r: {round(generator.burst_rate_response, 3)}\n"
            f"avg. burst duration: {generator.burst_duration_lam} ms\n"
        )

    ax.text(
        0.0,
        1.0,
        s,
        transform=ax.transAxes,
        ha="left",
        va="top",
        wrap=True,
    )

    ax.set_xticks([])
    ax.set_yticks([])
    sns.despine(left=True, bottom=True, ax=ax)

    return fig


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
    a: float | None,
    b: float | None,
    include_bursts: bool,
    burst_rate_baseline: float,
    burst_rate_response: float,
    burst_duration_lam: float,
    burst_alpha: float,
    burst_beta: float,
    burst_multiplier: float,
    n_trials: int,
) -> dict[str, Any]:
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
        burst_rate_response=burst_rate_response,
        burst_duration_lam=burst_duration_lam,
        burst_alpha=burst_alpha,
        burst_beta=burst_beta,
        burst_multiplier=burst_multiplier,
    )

    trial_activity = generator.generate(n_trials)

    fig = make_preview_figure(
        n_trials=n_trials,
        baseline_fr=baseline_fr,
        response_fr=response_fr,
        duration=duration,
        latency=latency,
        a=a,
        b=b,
        baseline_T=baseline_T,
        stimulus_T=stimulus_T,
        dt=dt,
        induce_refractory_period=induce_refractory_period,
        generator=generator,
        trial_activity=trial_activity,
    )

    image_base64 = fig_to_base64_png(fig)

    all_spikes = np.concatenate([t for t in trial_activity]) if len(trial_activity) else np.array([])
    n_spikes_total = int(sum(len(t) for t in trial_activity))
    mean_spikes_per_trial = float(n_spikes_total / n_trials) if n_trials > 0 else 0.0

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
        "n_spikes_total": n_spikes_total,
        "mean_spikes_per_trial": mean_spikes_per_trial,
        "first_spike_min": float(all_spikes.min()) if all_spikes.size else None,
        "last_spike_max": float(all_spikes.max()) if all_spikes.size else None,
    }

    return {
        "ok": True,
        "image_base64": image_base64,
        "stats": stats,
        "warnings": [],
    }