"""
plot_utils
==========

Create summary visualizations of a generated response.

Use:
----
n_trials = 10

generator = PoissonSpikeGenerator(...)
trial_activity = generator.generate(n_trials)
criteria = ResponseCriteria(...)

params = grab_fields(generator, criteria, n_trials)
fig = SpikeSummaryFigure(trial_activity, generator, criteria, params)
fig.build()
plt.show()
"""

from dataclasses import dataclass, fields
from datetime import datetime

import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

@dataclass
class SpikePlotParams: 
    n_trials: int
    baseline_fr: float
    response_fr: float
    latency: float
    duration: float
    baseline_T: float
    stimulus_T: float
    dt: float
    bin_width: float
    induce_refractory_period: bool
    a: float
    b: float
    direction: str
    multiple_correction: str
    baseline_T_stat: float
    proportion_active: float

def _filter_attrs(obj, cls):
    if obj is None: 
        return {}
    valid = {f.name for f in fields(cls)}
    return {k: getattr(obj, k) for k in valid if hasattr(obj, k)}

def grab_fields(generator, criteria, n_trials):
    return SpikePlotParams(n_trials=n_trials, direction=criteria.direction, multiple_correction=criteria.multiple_correction,
                         baseline_T_stat=criteria.baseline_T, proportion_active=criteria.proportion_active, bin_width=criteria.bin_width,
                         **_filter_attrs(generator, SpikePlotParams),)

class SpikeSummaryFigure: 
    def __init__(self, trial_activity, generator, criteria, params: SpikePlotParams):
        self.trial_activity = trial_activity
        self.generator = generator
        self.criteria = criteria
        self.params = params
        self.fig = None
        self.axes = None

    def build(self, figsize=(6,4), constrained=True):
        self.fig, self.axes = plt.subplot_mosaic(
            [["raster", "isi"],
            ["raster", "text"],
            ["r_t", "text"]], 
            empty_sentinel="empty", 
            width_ratios=[2, 1],
            height_ratios=[1,1,0.4],
            figsize=figsize,
            layout='constrained' if constrained else None,
        )
        self._plot_raster()
        self._plot_isi()
        self._plot_rt()
        self._plot_text_panel()
        self._add_header()
        return self.fig, self.axes
    
    def _plot_raster(self):
        ax = self.axes["raster"]
        ax.eventplot(self.trial_activity)
        ymin, ymax = ax.get_ylim()
        ax.vlines(self.params.baseline_T, ymin, ymax, colors="tab:orange")
        ax.set_xlim(0, self.params.baseline_T+self.params.stimulus_T)
        ax.set_xticklabels([])
        ax.set_yticks([])
        sns.despine(left=True, ax=ax)
    
    def _plot_isi(self):
        ax = self.axes["isi"]
        isis = np.concatenate([np.diff(t) for t in self.trial_activity])
        ax.hist(isis, bins=20)
        sns.despine(ax=ax)
        ax.set_xlabel("ISI [s]")
        ax.set_ylabel("count")

    def _plot_rt(self):
        ax = self.axes["r_t"]
        ax.plot(self.generator.r_t)
        ax.text(
            0.1, 1, "r(t)",
            transform=ax.transAxes,   # use axes coords, not data coords
            ha="left", va="top"      # align text to the top-right
        )
        ax.set_xlabel("time [ms]")
        ax.set_ylabel("fr [Hz]")
        sns.despine(ax=ax)

    def _plot_text_panel(self):
        ax = self.axes["text"]

        ax.set_in_layout(False) 
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_anchor('NW')

        s = (
            f"{self.params.n_trials} trials\n\n"
            f"params [time in sec]:\n"
            f"baseline FR: {self.params.baseline_fr} Hz\n"
            f"response FR: {self.params.response_fr} Hz\n"
            f"latency: {self.params.latency}\n"
            f"duration: {self.params.duration}\n"
            f"baseline_T: {self.params.baseline_T}\n"
            f"stimulus_T: {self.params.stimulus_T}\n"
            f"dt: {self.params.dt}\n"
            f"bin_width: {self.params.bin_width}\n"
            f"induce_refractory: {self.params.induce_refractory_period}\n"
            f"beta({self.params.a}, {self.params.b})\n"
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

    def _add_header(self):
        p = self.params
        header = (
            f"{datetime.today().strftime('%Y-%m-%d')}\n"
            f"-----------------------------------------\n"
            f"p-value:           {self.criteria.compute_pval():.3g}\n"
            f"% active trials:   {p.proportion_active:.2f}\n"
            f"direction:         {p.direction}\n"
            f"correction:        {p.multiple_correction}\n"
            f"baseline size [s]: {p.baseline_T_stat}\n"
        )

        left_ax = self.axes["raster"]
        bbox = left_ax.get_position()
        self.fig.text(
            bbox.x0,        # left edge of subplot
            bbox.y1 + 0.1, # a little above the subplot
            header,
            ha="left",
            va="bottom"
        )