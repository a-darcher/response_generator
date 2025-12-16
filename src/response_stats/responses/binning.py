import sys
sys.path.append("/home/al/Documents/code/generate_responses/generator")

import numpy as np

from response_stats.responses.config import ResponseConfig, ResponseData

def bin_baseline(cfg: ResponseConfig) -> np.ndarray:
    """
    Treats the entire baseline period as a single bin 
    and returns the spike count during this bin, scaled to Hz.

    Notes:
    - could generalize this to enable finer-grained binning.

    Returns
    -------
    baseline_hist : np.ndarray, shape (n_trials,)
        Spike counts in baseline per trial.
    """
    # count spikes during entire baseline period
    baseline_bins = [0, cfg.baseline_T] # e.g. [0, 1] for baseline of 1 second.
    baseline_hist = np.array([np.histogram(trial, baseline_bins)[0] 
                              for trial in cfg.trial_activity]).ravel()
    
    baseline_duration = baseline_bins[1] - baseline_bins[0]
    baseline = baseline_hist / baseline_duration # Hz

    if cfg.debug:
        assert sum(baseline_hist) == sum([sum(t <= cfg.baseline_T) for t in cfg.trial_activity]), "Binned baseline spikes do not match number of baseline spikes."
        print(f"Baseline duration: {baseline_duration} s")
        print(f"Mean, baseline: {np.mean(baseline)} Hz")
    return baseline
    

def _interleave_bins(cfg: ResponseConfig, 
                     bins_standard: np.ndarray, 
                     hist_standard: np.ndarray) -> np.ndarray:
    """
    Interleave the response period bins.
    Method:
        - bin twice, once using bins capped by the stimulus onset and offset with intervals of the given bin width
        and once using bins offset by half the bin width with caps of stimulus_onset + half bin width and stimulus_offset - half bin width. 
        - Alternate the bins for the final returned entry 

    Note that the output is not scaled to Hz. 
        
    Args:
        bins_standard (np.array): standard bin edges, e.g. [0, 100, 200, 300, 400, 500] for a bin size = 100
        hist_standard (np.array): spiking activity binned using bins_standard

    Returns:
        np.ndarray: shape (n_trials, (n_bins + (n_bins - 1))) spike counts with interleaved bins
    """
    
    bins_interleave = np.arange(cfg.stimulus_onset+(cfg.bin_width/2), (cfg.stimulus_onset + cfg.stimulus_T), cfg.bin_width)
    hist_interleave = np.array([np.histogram(trial, bins_interleave)[0] for trial in cfg.trial_activity])
    
    interleaved = np.zeros((len(cfg.trial_activity), len(bins_standard)+len(bins_interleave)-2), int)
    interleaved[:, ::2] = hist_standard
    interleaved[:, 1::2] = hist_interleave

    if cfg.debug:
        lower = cfg.stimulus_onset + cfg.bin_width/2
        upper = cfg.stimulus_onset + cfg.stimulus_T - cfg.bin_width/2
        assert (hist_interleave).sum() == sum([sum((t >= lower) & (t <= upper)) for t in cfg.trial_activity]), "Binned stimulus spikes (interleaved period) do not match number of total stimulus spikes."
        assert interleaved.sum() == hist_interleave.sum() + hist_standard.sum(), "Interleaved matrix does not included the expected number of spikes."

    return interleaved

def bin_spikes(cfg: ResponseConfig):
    """
    Bin spikes during the stimulus period.
    Can optionally interleave the bins by setting `interleave_response_bins` to True in the class initialization.
    See _interleave_bins() for details. 

    Scales the spike counts to Hz. 
    Spikes with times exactly equal to the stimulus onset are not included, and are counted by the baseline period.

    Returns
    -------
    np.ndarray : shape (n_trials, n_bins) spike counts (Hz).
    """
    # note: onset of bins is baseline time + dt, to allow border-spikes to be counted only in the baseline
    bins = np.arange(cfg.stimulus_onset + cfg.dt, (cfg.stimulus_onset + cfg.stimulus_T)+cfg.bin_width, cfg.bin_width) 
    hist = np.array([np.histogram(trial, bins)[0] for trial in cfg.trial_activity])
    
    if cfg.interleave_response_bins:
        binned_spikes = _interleave_bins(cfg, bins, hist)
    else:
        binned_spikes = hist

    # convert to rate per second, from rate per (bin width)
    response = binned_spikes / cfg.bin_width 

    if cfg.debug:
        # just checking the OG hist, not the interleaved, which ~double-counts spikes.
        assert hist.sum() == sum([sum(t >= cfg.stimulus_onset + cfg.dt) for t in cfg.trial_activity]), "Binned stimulus spikes (full period) do not match number of total stimulus spikes."
        print(f"Response duration, edge-corrected: {bins[-1]-bins[0]} s")
        print(f"Mean, response: {np.mean(response)} Hz")
    return response

def make_response_data(cfg: ResponseConfig) -> ResponseData:
    baseline_hist = bin_baseline(cfg)
    response_hist = bin_spikes(cfg)
    return ResponseData(cfg=cfg, baseline_hist=baseline_hist, response_hist=response_hist)