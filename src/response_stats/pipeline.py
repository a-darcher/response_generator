"""
pipeline.py — simulate a set of responses using parameters from a config file.

Author: Alana Darcher
Email: darcher@tuta.io
Date: 2025-Nov-27

Example Usage:
$ python3 pipeline.py --config configs/test.yaml

"""

from __future__ import annotations
from typing import List, Dict, Any
import yaml

import shutil

from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

import numpy as np
import pandas as pd
from tqdm import tqdm
from scipy.io import savemat 
import matplotlib.pyplot as plt
import seaborn as sns

from response_stats.config import default_seed
from response_stats.config_plot import *
from response_stats.matlab_io import *
from response_stats.generators import PoissonSpikeGenerator

@dataclass(frozen=True)
class SimulationConfig: 
    n_samples: int
    save_dir: Path
    save_language: str

    # baseline- or response-type
    response_type: str

    # trial params
    trial_range: int | tuple | list

    # time params
    baseline_T: float
    stimulus_T: float
    dt: float



    # peak response firing rate params
    gain_response_fr_threshold: int
    gain_response_fr_scale: int

    # response shape - beta params
    beta_a_range: tuple | list
    beta_multiplier_range: tuple | list

    # response duration params
    duration_range: float | tuple | list
    
    # delay in response onset param
    latency_range: float | tuple | list
    
    induce_refractory_period: bool

    # supplementary trials params
    generate_supplementary_trials: bool
    supplementary_threshold: int
    supplementary_default_count: int
    supplementary_default_factor: int

    seed: int = default_seed

    # baseline firing rate params
    baseline_threshold: int | bool = False
    baseline_scale: int | bool = False
    baseline_range: tuple | list | bool = False

    
    @staticmethod
    def from_yaml(path: Path) -> "SimulationConfig":
        """Construct a SimulationConfig dataclass from a config file.

        Args:
            path (Path): path to the config file

        Returns:
            SimulationConfig: dataclass instance
        """
        with open(path, "r") as f:
            d = yaml.safe_load(f)
        
        d["save_dir"] = Path(d["save_dir"])
        return SimulationConfig(**d)

class ResponseSimulator:
    def __init__(self, cfg: SimulationConfig):
        self.cfg = cfg
        self.rng = np.random.default_rng(seed=cfg.seed)

        self.time_str = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
        self.dir_name = f"{cfg.response_type}_trials{cfg.trial_range}"
        self.save_dir = cfg.save_dir / self.dir_name
        (self.save_dir / "example_responses").mkdir(parents=True, exist_ok=True)

    def _handle_baseline_firing_rates(self):
        if self.cfg.baseline_threshold and self.cfg.baseline_scale:
            u = self.rng.uniform(size=self.cfg.n_samples)
            fr_baseline = self.cfg.baseline_threshold - self.cfg.baseline_scale * np.log(u)

        elif isinstance(self.cfg.baseline_range, (list, tuple)):
            fr_baseline = self.rng.uniform(low=self.cfg.baseline_range[0], 
                                           high=self.cfg.baseline_range[1],
                                           size=self.cfg.n_samples)
        
        return fr_baseline
    
    def _handle_trial_counts(self):
        if np.isscalar(self.cfg.trial_range):
            trial_counts = np.full(self.cfg.n_samples, self.cfg.trial_range, dtype=np.int64)
        elif isinstance(self.cfg.trial_range, (list, tuple)):
            trial_counts = self.rng.integers(
                self.cfg.trial_range[0], 
                self.cfg.trial_range[1], 
                size=self.cfg.n_samples, 
                endpoint=True)
        else:
            raise TypeError("trial_range must be a scalar or a tuple.")
        return trial_counts
    
    def _handle_extra_trial_counts(self, n_trials):
        if n_trials < self.cfg.supplementary_threshold:
            n_supplement_trials = self.cfg.supplementary_default_count
        else:
            n_supplement_trials = n_trials * self.cfg.supplementary_default_factor
        return n_supplement_trials

    def _handle_response_firing_gain(self, trial_list):
        trial_list = np.asarray(trial_list)
        fr_responses = self.cfg.gain_response_fr_threshold - self.cfg.gain_response_fr_scale * np.log(self.rng.uniform(size=len(trial_list)))
        return fr_responses
    
    def _handle_response_type(self, n_trials_list, fr_baseline):
        """Set generation parameters according to response type. 
        Types: 
        - 'response' - simulates a stimulus-elicited change in firing by varying the probability of response after onset
        - 'baseline' - no change in firing after stimulus 'onset'

        Args:
            n_trials_list (list): trials counts for each sample to be generated
            fr_baseline (float): firing rate during the baseline period

        Raises:
            TypeError: non-implemented response type

        Returns:
            fr_response: np.array, peak firing rate during the response period for each trial 
            beta_a_s: np.array, alpha parameters for specifying a Beta distribution for each trial's rate function
            beta_b_s: np.array, beta parameters for specifying a Beta distribution for each trial's rate function
        """
        cfg = self.cfg

        if cfg.response_type == "response":
            ratios = self._handle_response_firing_gain(n_trials_list)
            fr_response = (fr_baseline + 1) * ratios # fr_baseline altered to be > 1 for a clear response.

            beta_a_s = self.rng.uniform(low=cfg.beta_a_range[0], high=cfg.beta_a_range[1], size=cfg.n_samples)
            beta_multiplier_s = self.rng.uniform(cfg.beta_multiplier_range[0], cfg.beta_multiplier_range[1], size=cfg.n_samples)
            beta_b_s = beta_a_s * beta_multiplier_s

        elif cfg.response_type == "baseline":
            fr_response = fr_baseline
            beta_a_s = np.full(len(n_trials_list), None)
            beta_b_s = np.full(len(n_trials_list), None)
        else:
            raise TypeError

        return fr_response, beta_a_s, beta_b_s
    
    def _handle_durations(self,) -> np.array:
        """Handle response duration input. 
        Durations can either be a scalar (float) or a tuple giving the edges of a range from which durations should be drawn.

        Raises:
            ValueError: can only input either a scalar value or a tuple, but not both.

        Returns:
            np.array: duration of the response for each trial
        """
        if np.isscalar(self.cfg.duration_range):
            durations = np.full(self.cfg.n_samples, self.cfg.duration_range)
        elif isinstance(self.cfg.duration_range, (list, tuple)):
            durations = self.rng.uniform(self.cfg.duration_range[0], self.cfg.duration_range[1], size=self.cfg.n_samples)
        else:
            raise TypeError("duration_range must be a scalar or a tuple.")
        return durations
    
    def _handle_latencies(self,) -> np.array:
        if np.isscalar(self.cfg.latency_range):
            latencies = np.full(self.cfg.n_samples, self.cfg.latency_range)
        elif isinstance(self.cfg.latency_range, (list, tuple)):
            latencies = self.rng.uniform(self.cfg.latency_range[0], self.cfg.latency_range[1], size=self.cfg.n_samples)
        else:
            raise TypeError("latency_range must be a scalar or a tuple.")
        return latencies

    def run(self) -> pd.DataFrame:
        """Runner for simulating the specified batch of units.

        Returns:
            pd.DataFrame: collection of simulating trial-wise activity and collected parameters
        """
        cfg = self.cfg
        rng = self.rng

        fr_baseline = self._handle_baseline_firing_rates()
        trial_counts = self._handle_trial_counts()

        if cfg.generate_supplementary_trials:
            supplement_trials_counts = np.vectorize(self._handle_extra_trial_counts)(trial_counts)
        else:
            supplement_trials_counts = 0
        
        fr_response, beta_a_s, beta_b_s = self._handle_response_type(trial_counts, fr_baseline)
        durations = self._handle_durations()
        latencies = self._handle_latencies()

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

            if i < 10:
                self._plot_example(i, n_trials, baseline_fr, response_fr, duration, latency, a, b, generator, trial_activity)

        df["rasters"] = rasters
        if cfg.generate_supplementary_trials:
            df["supp_rasters"] = supplement_trials
        
        return df
        
    # plot functions
    def _plot_trial_hist(self, n_trial_responses: np.ndarray) -> None:
        """Plot the distribution of the number of trials in a simulated batch. 

        Args:
            n_trial_responses (np.ndarray): list of trial amounts
        """
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
        i: int,
        n_trials: int,
        baseline_fr: float,
        response_fr: float,
        duration: float,
        latency: float,
        a: float | None,
        b: float | None,
        generator: PoissonSpikeGenerator,
        trial_activity: List[np.ndarray],
    ) -> None:
        """Plot an example response.

        Args:
            i (int): sample index
            n_trials (int): number of trials in sample
            baseline_fr (float): baseline firing rate
            response_fr (float): peak response firing rate
            duration (float): duration of the response
            a (float | None): Beta distribution alpha param
            b (float | None): Beta distribution beta param
            generator (PoissonSpikeGenerator): unit's class instance
            trial_activity (List[np.ndarray]): simulated trial-wise spiking activity
        """
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

        if bool(a):
            s = (
                f"{n_trials} trials\n\n"
                f"params [time in sec]:\n"
                f"baseline FR: {round(baseline_fr, 3)} Hz\n"
                f"response FR: {round(response_fr, 3)} Hz\n"
                f"latency: {round(latency, 3)}\n"
                f"duration: {round(duration, 3)} s\n"
                f"baseline_T: {cfg.baseline_T} s\n"
                f"stimulus_T: {cfg.stimulus_T} s\n"
                f"dt: {cfg.dt} s\n"
                f"induce_refractory: {cfg.induce_refractory_period}\n"
                f"beta({round(a, 3)}, {round(b, 3)})"
            )
        else:
            s = (
                f"{n_trials} trials\n\n"
                f"params [time in sec]:\n"
                f"baseline FR: {round(baseline_fr, 3)} Hz\n"
                f"response FR: {round(response_fr, 3)} Hz\n"
                f"latency: {round(latency, 3)}\n"
                f"duration: {round(duration, 3)} s\n"
                f"baseline_T: {cfg.baseline_T} s\n"
                f"stimulus_T: {cfg.stimulus_T} s\n"
                f"dt: {cfg.dt} s\n"
                f"induce_refractory: {cfg.induce_refractory_period}\n"
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
                
        if bool(a):
            fname = f"{i}_{n_trials}trials_{int(baseline_fr)}bFR_{int(response_fr)}rFR_{round(duration,2)}duration_beta{round(a,2)}-{round(b,2)}.png"
        else:
            fname = f"{i}_{n_trials}trials_{int(baseline_fr)}bFR_{int(response_fr)}rFR_{round(duration,2)}duration.png"
        fig.savefig(self.save_dir / "example_responses" / fname)
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

def _is_sequence(x):
    return isinstance(x, (list, tuple, np.ndarray))

def _as_numeric_vector(x):
    """Convert x to a 1D float vector (numpy array)."""
    v = np.asarray(x, dtype=float).ravel()
    return v

def _as_cell_of_scalars(x):
    """Convert 1D numeric x -> numpy object array of python floats (cell-of-scalars)."""
    v = np.asarray(x, dtype=float).ravel()
    return np.array([float(z) for z in v], dtype=object)

def _as_cell_of_vectors(seq):
    """
    Convert seq (sequence of segments) -> numpy object array,
    each element is a 1D float vector (cell-of-vectors).
    """
    out = np.empty(len(seq), dtype=object)
    for i, seg in enumerate(seq):
        out[i] = _as_numeric_vector(seg)
    return out

def _force_matlab_cell_structure(df, col="rasters"):
    src = df[col].to_numpy(dtype=object)

    # Outer cell: one entry per trial
    out = np.empty(src.shape[0], dtype=object)

    for i, r in enumerate(src):
        if r is None:
            out[i] = np.empty(0, dtype=object)
            continue

        # If r is a numpy array with dtype != object and ndim == 1: it's flat numeric
        if isinstance(r, np.ndarray) and r.dtype != object:
            out[i] = _as_cell_of_scalars(r)
            continue

        # If r is a list/tuple or object-array, decide whether it’s nested:
        # nested means: at least one element is itself a sequence/array (and not a string)
        if _is_sequence(r):
            # Make it easy to iterate elements (works for list/tuple/object-array)
            elems = list(r)

            nested = any(_is_sequence(e) and not isinstance(e, (str, bytes)) for e in elems)

            if nested:
                # Preserve grouping: cell of vectors
                out[i] = _as_cell_of_vectors(elems)
            else:
                # Flat: cell of scalars
                out[i] = np.array([float(e) for e in elems], dtype=object)
            continue

        # Fallback: scalar
        out[i] = np.array([float(r)], dtype=object)

    mat_dict = {c: df[c].to_numpy() for c in df.columns}
    mat_dict[col] = out
    return mat_dict

def _parse_save_by_language(cfg, save_path, df, fname):
    if cfg.save_language == "python":
        df.to_parquet(save_path / f"{fname}.parquet")
    elif cfg.save_language == "matlab":
        mat_dict = _force_matlab_cell_structure(df)
        savemat(save_path / f"{fname}.mat", {"data": mat_dict})
    elif cfg.save_language == "both":
        df.to_parquet(save_path / f"{fname}.parquet")

        # force cell structure for single-spike trials
        mat_dict = _force_matlab_cell_structure(df)

        savemat(save_path / f"{fname}.mat", {"data": mat_dict})

def _copy_config_file(config_path, save_path):
    shutil.copy(config_path, f"{save_path}/run_config.yaml")

def main(argv=None):
    args = _parse_cli_args(argv)
    cfg = SimulationConfig.from_yaml(args["config_path"])

    rs = ResponseSimulator(cfg)
    df = rs.run()
    
    config_fname = Path(args["config_path"]).name
    fname = f"{cfg.response_type}_{cfg.n_samples}samples_{config_fname}-config_{rs.time_str}"
    _parse_save_by_language(cfg, rs.save_dir, df, fname)
    _copy_config_file(args["config_path"], rs.save_dir)
    
if __name__ == "__main__":
    main()