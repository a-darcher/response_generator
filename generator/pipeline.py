from __future__ import annotations
from typing import Optional, Tuple, List, Iterable, Dict, Any
import yaml
import sys
sys.path.append("/home/al/Documents/code/generate_responses/generator")

from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

import numpy as np
import pandas as pd
import tqdm as tqdm
from scipy.io import savemat 
import matplotlib.pyplot as plt
import seaborn as sns

from config import default_seed
from config_plot import *
from matlab_io import *
from generators import PoissonSpikeGenerator
from stats import ResponseCriteria 

@dataclass(frozen=True)
class SimulationConfig: 
    n_samples: int
    response_type: str = "response"

    # trial params
    min_trial_num: int
    scale_trial: int

    # baseline firing rate params
    threshold: int
    scale: int

    # beta params
    beta_a_range: tuple
    beta_multiplier_range = tuple

    # response params
    duration_range: tuple
    latency: float
    duration: float
    baseline_T: float
    stimulus_T: float
    df: float = 0.001
    induce_refractory_period: bool = True

    gain_low_trial = 20
    gain_high_trial = 10

    # supplementary trials params
    generate_supplementary_trials: bool = True
    supplementary_threshold: int = 50
    supplementary_default_count: int = 200
    supplementary_default_factor: int = 5

    seed: int = default_seed
    save_dir: Path

    @staticmethod
    def from_yaml(path: Path) -> "SimulationConfig":
        with open(path, "r") as f:
            d = yaml.safe_load(f)
        
        d["save_dir"] = Path(d["save_dir"])
        return SimulationConfig(**d)

class ResponseSimulator:
    def __init__(self, cfg: SimulationConfig):
        self.cfg = cfg
        self.rng = np.random.default_rng(seed=cfg.seed)
        self.save_dir = cfg.save_dir
        (self.save_dir / "example_responses").mkdir(parents=True, exist_ok=True)

    def determine_response_firing_gain(self, trial_list):
        """Set the increase in firing rate for the response period conditioned on the number of trials.

        Args:
            trial_list (list): list containing the number of trials for all simulations

        Returns:
            np.array: 1 x n_samples, peak firing rate during the response period for a given sample
        """
        trial_list = np.asarray(trial_list)
        fr_responses = np.empty_like(trial_list, dtype=float)

        low_trials_mask = trial_list <= 10
        high_trials_mask = ~low_trials_mask

        fr_responses[low_trials_mask] = self.gain_low_trial - 3 * np.log(self.rng.uniform(size=low_trials_mask.sum()))
        fr_responses[high_trials_mask] = self.gain_high_trial - 3 * np.log(self.rng.uniform(size=high_trials_mask.sum()))
        
        return fr_responses
    
    def determine_extra_trial_counts(self, n_trials):
        if n_trials < self.cfg.supplementary_threshold:
            n_supplement_trials = self.cfg.supplementary_default_count
        else:
            n_supplement_trials = n_trials * self.cfg.supplementary_default_factor
        return n_supplement_trials

    def run(self) -> pd.DataFrame:
        cfg = self.cfg
        rng = self.rng

        u = rng.uniform(size=cfg.n_samples)
        fr_baseline = cfg.threshold - cfg.scale * np.log(u)

        n_trials_no_response = np.array(cfg.min_trial_num - cfg.scale_trial * np.log(u), dtpye=int)
        if cfg.generate_supplementary_trials:
            n_supplement_trials = np.vectorize(self.determine_extra_trial_counts)(n_trials_no_response)

        df = pd.DataFrame({
            "n_trials": n_trials_no_response.astype(dtype=np.int8),
            "response": np.zeros(cfg.n_samples, dtype=np.int8),
            "fr_baseline": fr_baseline.astype(float),
            "fr_response": fr_baseline.astype(float),
            "latency": np.full(cfg.n_samples, cfg.latency, dtype=float),
            "duration": np.full(cfg.n_samples, cfg.duration, dtype=float),
            "time_baseline": np.full(cfg.n_samples, cfg.baseline_T, dtype=float),
            "time_stimulus": np.full(cfg.n_samples, cfg.stimulus_T, dtype=float),
            "refractory_period_induced": np.ones(cfg.n_samples, dtype=np.int8),
        })
        
        rasters = [None] * cfg.n_samples
        if cfg.generate_supplementary_trials:
            supplement_trials = [None] * cfg.n_samples

        for i, fr in enumerate(tqdm(fr_baseline)):
            n_trials = n_trials_no_response[i]
            n_supplement_trials = self.determine_extra_trial_counts(n_trials)

            baseline_fr  = fr
            response_fr  = fr

            generator = PoissonSpikeGenerator(
            baseline_fr=baseline_fr,
            response_fr=response_fr,
            latency=cfg.latency,
            duration=cfg.duration,
            baseline_T=cfg.baseline_T,
            stimulus_T=cfg.stimulus_T,
            dt=cfg.dt,
            induce_refractory_period=cfg.induce_refractory_period,
            rng=rng,
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

        df["rasters"] = rasters
        if cfg.generate_supplementary_trials:
            df["supp_rasters"] = supplement_trials
        
        return df
        
    # plot functions
    def _plot_trial_hist(self, n_trial_responses: np.ndarray) -> None:
        ts = f"{datetime.today():%Y-%m-%d}"
        plt.figure(figsize=(5, 3))
        plt.hist(n_trial_responses, bins=100)
        plt.title(f"distribution of trial amounts\n across {self.cfg.n_samples} simulated responses")
        plt.xlabel("# of trials")
        plt.ylabel("frequency")
        sns.despine()
        plt.savefig(self.save_dir / f"{ts}_distribution_trials.png")
        plt.close()

    def _plot_example(
        self,
        *,
        i: int,
        n_trials: int,
        baseline_fr: float,
        response_fr: float,
        duration: float,
        a: float,
        b: float,
        generator: PoissonSpikeGenerator,
        trial_activity: List[np.ndarray],
    ) -> None:
        cfg = self.cfg


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
        ax.vlines(0, ymin, ymax, colors="tab:orange")
        ax.set_xlim(-1*cfg.baseline_T, cfg.stimulus_T)
        ax.set_xticklabels([])
        ax.set_yticks([])
        sns.despine(left=True, ax=ax)

        ax = axes["isi"]

        try:
            isis = np.concatenate([np.diff(t) for t in trial_activity])
        except ValueError:
            isis = np.zeros(1)
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
            f"baseline FR: {round(baseline_fr, 3)} Hz\n"
            f"response FR: {round(response_fr, 3)} Hz\n"
            f"latency: {cfg.latency}\n"
            f"duration: {duration}\n"
            f"baseline_T: {cfg.baseline_T}\n"
            f"stimulus_T: {cfg.stimulus_T}\n"
            f"dt: {cfg.dt}\n"
            f"induce_refractory: {cfg.induce_refractory_period}\n"
            f"beta({round(a, 3)}, {round(b, 3)})"

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
                
        fname = f"{i}_{n_trials}trials_{int(baseline_fr)}bFR_{int(response_fr)}rFR_{round(duration,2)}duration_beta{round(a,2)}-{round(b,2)}.png"
        fig.savefig(cfg.save_dir / "example_responses" / fname)
        plt.close(fig)

# convenience functions
def run(config: SimulationConfig) -> pd.DataFrame:
    return ResponseSimulator(config).run()
            
def _parse_cli_args(argv= None) -> Dict[str, Any]:
    import argparse

    p = argparse.ArgumentParser(description="Run spike simulation pipeline.")
    p.add_argument("--config", type=Path, required=True,
                   help="Path to YAML configuration file.")
    args = p.parse_args(list(argv) if argv is not None else None)
    return {"config_path": args.config}

def main(argv=None):
    args = _parse_cli_args(argv)
    cfg = SimulationConfig.from_yaml(args["config_path"])
    df = run(cfg)
    
if __name__ == "__main__":
    main()