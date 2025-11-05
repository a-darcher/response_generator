import numpy as np
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns

from tqdm import tqdm

from config_plot import *


def plot_response(generator, criterion):
    baseline_fr = generator.baseline_fr
    response_fr = generator.response_fr
    latency = generator.latency
    duration = generator.duration
    dt = generator.dt
    baseline_T = generator.baseline_T
    stimulus_T = generator.stimulus_T
    total_bins = generator.total_bins
    induce_refractory_period = generator.induce_refractory_period
    kappa = generator.kappa
    r_t = generator.r_t
    p = generator.p

    debug = criterion.debug
    trial_activity = criterion.trial_activity
    baseline_T_stat = criterion.baseline_T
    stimulus_T = criterion.stimulus_T
    stimulus_onset = criterion.stimulus_onset
    bin_width = criterion.bin_width
    dt = criterion.dt
    direction = criterion.direction
    proportion_active = criterion.proportion_active
    multiple_correction = criterion.multiple_correction
    baseline_hist = criterion.baseline_hist
    interleaved = criterion.interleaved
    pvals_binwise = criterion.pvals_binwise
    direction_of_bin = criterion.direction_of_bin
    
    n_trials = len(trial_activity)

    fig, axes = plt.subplot_mosaic(
        [
            ["raster", "isi"],
            ["raster", "text"],
            ["r_t", "text"]
        ], 
        empty_sentinel="empty", 
        width_ratios=[2, 1],
        height_ratios=[1,1,0.4],
        figsize=(6,4),
        layout='constrained',

    )

    ax = axes["raster"]
    ax.eventplot(trial_activity)
    ymin, ymax = ax.get_ylim()
    ax.vlines(stimulus_onset, ymin, ymax, colors="tab:orange")
    ax.set_xlim(0, stimulus_onset+stimulus_T)
    ax.set_xticklabels([])
    ax.set_yticks([])
    sns.despine(left=True, ax=ax)

    ax = axes["isi"]
    isis = np.concatenate([np.diff(t) for t in trial_activity])
    ax.hist(isis, bins=20)
    sns.despine(ax=ax)
    ax.set_xlabel("ISI [s]")
    ax.set_ylabel("count")

    ax = axes["r_t"]
    ax.plot(generator.r_t)
    ax.text(
        0.1, 1, "r(t)",
        transform=ax.transAxes,   # use axes coords, not data coords
        ha="left", va="top"      # align text to the top-right
    )
    ax.set_xlabel("time [ms]")
    ax.set_ylabel("fr [Hz]")
    sns.despine(ax=ax)

    ax = axes["text"]

    ax.set_in_layout(False) 
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_anchor('NW')

    s = (
        f"{n_trials} trials\n\n"
        f"params [time in sec]:\n"
        f"baseline FR: {baseline_fr} Hz\n"
        f"response FR: {response_fr} Hz\n"
        f"latency: {latency}\n"
        f"duration: {duration}\n"
        f"baseline_T: {baseline_T}\n"
        f"stimulus_T: {stimulus_T}\n"
        f"dt: {dt}\n"
        f"bin_width: {bin_width}\n"
        f"induce_refractory: {induce_refractory_period}"
    )

    ax.text(
        0.0, 1.0,
        s,
        transform=ax.transAxes,
        ha="left",
        va="top",
        wrap=True
    )

    ax.set_xticks([])
    ax.set_yticks([])

    sns.despine(left=True, bottom=True, ax=ax)

    s = (
        f"{datetime.today().strftime('%Y-%m-%d')}\n"
        f"-----------------------------------------\n"
        f"p-value:           {criterion.compute_pval():.3g}\n"
        f"% active trials:   {proportion_active:.2f}\n"
        f"direction:         {direction}\n"
        f"correction:        {multiple_correction}\n"
        f"baseline size [s]: {baseline_T_stat}\n"
    )
    left_ax = axes["raster"]
    bbox = left_ax.get_position()
    fig.text(
        bbox.x0,        # left edge of subplot
        bbox.y1 + 0.1, # a little above the subplot

        s,
        ha="left",
        va="bottom"
    )

    plt.show()