from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

from response_stats.pipeline import SimulationConfig, ResponseSimulator, _force_matlab_cell_structure, _parse_save_by_language, _as_cell_of_scalars, _as_numeric_vector, _is_sequence, _as_cell_of_vectors
from response_stats.generators import PoissonSpikeGenerator

from response_stats.plot_utils import *


from scipy.ndimage import gaussian_filter

baseline_frs = np.arange(0.1, 15.1, 0.2)
response_frs = np.arange(0.1, 50, 0.2)

fr_pairs = np.array([[b, r] for b in baseline_frs for r in response_frs])
n_samples = len(fr_pairs)
print(f"# samples: {n_samples}")

fr_baseline = fr_pairs[:,0]
fr_response = fr_pairs[:,1]

burst_rate_baseline_all = np.ones(n_samples) * 0.5
burst_rate_response_all = np.ones(n_samples) * 15

save_dir = Path("/media/al/darch/response_stats/datasets/uniform_sampling_incl_negative_bursts")

trial_ranges = [
    [100, 500],
    [15, 100],
    [5, 15],
]

for trial_range in trial_ranges:
    print(trial_range)

    cfg = SimulationConfig(
    # =========================
    # General
    # =========================
    n_samples=n_samples,
    save_dir=save_dir,
    save_language="both",

    # =========================
    # Response type
    # =========================
    response_type="response",

    # =========================
    # Trial parameters
    # =========================
    trial_range=trial_range,

    # =========================
    # Time parameters
    # =========================
    baseline_T=2.0,
    stimulus_T=2.0,
    dt=0.001,

    # =========================
    # Response shape (beta params)
    # =========================
    beta_a_range=[1, 1.5],
    beta_multiplier_range=[1.5, 2],

    # =========================
    # Response duration
    # =========================
    duration_range=[0.25, 0.7],

    # =========================
    # Response latency
    # =========================
    latency_range=[0.25, 0.41],

    induce_refractory_period=True,

    # =========================
    # Supplementary trials
    # =========================
    generate_supplementary_trials=True,
    supplementary_default_count=200,

    # =========================
    # Random seed
    # =========================
    seed=73,

    # =========================
    # Baseline firing rate
    # =========================
    baseline_threshold=False,
    baseline_scale=False,
    baseline_range=[0, 15],

    # =========================
    # Peak response firing rate
    # =========================
    response_fr_sampler="uniform",
    response_fr_method="linear_function",
    response_fr_scale=False,
    response_fr_max=60,

    # =========================
    # Gain response function
    # =========================
    gain_response_fixed=False,
    gain_response_y=False,
    gain_response_high=False,
    gain_response_e=False,

    # =========================
    # Linear response function
    # =========================
    linear_response_slope=1,
    linear_response_offset=0,
    

    # =========================
    # Burst Params
    # =========================
    include_bursts=True,
    burst_rate_baseline=0,
    burst_rate_response=15,
    burst_rate_baseline_scale=1,
    burst_rate_response_scale=2,
    burst_duration_lam=150,
    burst_response_time_factor=5,
    burst_alpha=1.5,
    burst_beta=3,
    burst_multiplier=15,
    burst_rate_factor= 0.25
    
)

    rng = np.random.default_rng(seed=cfg.seed)

    # create instance of ResponseSimulator to obtain the other randomized parameters.
    rs = ResponseSimulator(cfg)
    trial_counts = rs._handle_trial_counts()
    supplement_trials_counts = rs._handle_supplementary_trial_counts(trial_counts)

    _, beta_a_s, beta_b_s = rs._handle_response_type(trial_counts, fr_baseline)

    durations = rs._handle_durations()
    latencies = rs._handle_latencies()

    response_bool = 1 if cfg.response_type == "response" else 0

    df = pd.DataFrame({
        "n_trials": trial_counts.astype(dtype=np.int32),
        "n_supp_trials": supplement_trials_counts.astype(dtype=np.int32),
        "response": np.full(cfg.n_samples, response_bool, dtype=str),
        "fr_baseline": fr_baseline.astype(float),
        "fr_response": fr_response.astype(float),
        "latency": latencies.astype(float),
        "duration": durations.astype(float),
        "time_baseline": np.full(cfg.n_samples, cfg.baseline_T, dtype=float),
        "time_stimulus": np.full(cfg.n_samples, cfg.stimulus_T, dtype=float),
        "refractory_period_induced": np.full(cfg.n_samples, cfg.induce_refractory_period, dtype=np.int8),
        "beta_a": beta_a_s.astype(float),
        "beta_b": beta_b_s.astype(float),
        "baseline_burst_rate": burst_rate_baseline_all.astype(float),
        "response_burst_rate": burst_rate_response_all.astype(float),
    })

    rasters = [None] * cfg.n_samples
    if cfg.generate_supplementary_trials:
        supplement_trials = [None] * cfg.n_samples

    for i, fr in enumerate(tqdm(fr_baseline)):
        n_trials = trial_counts[i]
        n_supplement_trials = supplement_trials_counts[i]

        baseline_fr  = fr
        response_fr  = fr_response[i]

        duration = durations[i]
        latency = latencies[i]
        a = beta_a_s[i]
        b = beta_b_s[i]

        burst_rate_baseline = burst_rate_baseline_all[i]
        burst_rate_response = burst_rate_response_all[i]

        generator = PoissonSpikeGenerator(
        baseline_fr=baseline_fr,
        response_fr=response_fr,
        latency=latency,
        duration=duration,
        baseline_T=cfg.baseline_T,
        stimulus_T=cfg.stimulus_T,
        dt=cfg.dt,
        induce_refractory_period=cfg.induce_refractory_period,
        rng=rng,
        a=a,
        b=b, 
        include_bursts=cfg.include_bursts, 
                burst_rate_baseline=burst_rate_baseline, 
                burst_rate_factor=cfg.burst_rate_factor,
                burst_rate_response=burst_rate_response, 
                burst_response_time_factor=cfg.burst_response_time_factor, 
                # trial-wise burst params
                burst_duration_lam=cfg.burst_duration_lam,
                burst_alpha=cfg.burst_alpha, 
                burst_beta=cfg.burst_beta,
                burst_multiplier=cfg.burst_multiplier,
        )

        # generate trials
        trial_activity = generator.generate(n_trials)
        supp_trial_activity = generator.generate(n_supplement_trials)

        # rescale
        trial_activity = [t - cfg.baseline_T for t in trial_activity]    
        supp_trial_activity = [np.array(t) - cfg.baseline_T for t in supp_trial_activity]

        rasters[i] = trial_activity
        if cfg.generate_supplementary_trials:
            supplement_trials[i] = supp_trial_activity

        if i < 50:
            bin_size = 25 / 1000
            sigma = 1

            bins = np.arange(generator.baseline_T * -1, generator.stimulus_T + (bin_size), bin_size)
            bin_centers = np.convolve(bins, np.ones(2) / 2, mode="valid")
            binned_spikes = np.array([np.histogram(e, bins=bins)[0] for e in trial_activity]) / bin_size
            mean_fr = np.mean(binned_spikes, axis=0)
            smooth_fr = np.mean(gaussian_filter(binned_spikes, sigma=sigma), axis=0)

            mean_fr_baseline = smooth_fr[(bin_centers < 0) ]

            if baseline_fr > response_fr:
                # mean response period is latency + duration
                # peak is the minimum
                mean_fr_response = smooth_fr[(bin_centers > latency) & (bin_centers < (latency + duration))]
                peak = np.min(mean_fr_response)
            elif np.isclose(response_fr, baseline_fr, atol=1):
                # mean response period is the entire response section, to match the baseline period
                # peak is the average
                mean_fr_response = smooth_fr[(bin_centers > 0) & (bin_centers < 2)]
                peak = np.mean(mean_fr_response)
            else:
                # mean response period is latency + duration
                # peak is the max during this section
                mean_fr_response = smooth_fr[(bin_centers > latency) & (bin_centers < (latency + duration))]
                peak = np.max(mean_fr_response)

            print(f"{i}     measured baseline FR: {np.mean(mean_fr_baseline)}   measured response peak: {peak}  measured response mean: {np.mean(mean_fr_response)}")
            rs._plot_example(i, n_trials, baseline_fr, response_fr, duration, latency, a, b, generator, trial_activity)

    df["rasters"] = rasters
    if cfg.generate_supplementary_trials:
        df["supp_rasters"] = supplement_trials

    config_fname = f"fromNotebook"
    fname = f"{cfg.response_type}_{cfg.n_samples}samples_{config_fname}-config_{rs.time_str}"
    _parse_save_by_language(cfg, rs.save_dir, df, fname)