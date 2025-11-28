"""
config.py - dataclass objects for specify response search parameters

Author: Alana Darcher
Email: darcher@tuta.io
Date: 2025-Nov-28

"""

from typing import Literal
from dataclasses import dataclass

import numpy as np

Direction = Literal["positive", "negative"]
Correction = Literal["simes", "none"]

@dataclass(frozen=True)
class ResponseConfig:
    trial_activity: list[np.ndarray]
    baseline_T: float
    stimulus_T: float
    stimulus_onset: int
    bin_width: float
    dt: float

    direction: Direction = "positive"
    proportion_active: float = 1/3
    multiple_correction: Correction = "simes"
    interleave_response_bins: bool = True
    smooth_response_bins: None | bool = False

    debug: bool = False

@dataclass
class ResponseData:
    cfg: ResponseConfig
    baseline_hist: np.ndarray
    response_hist: np.ndarray

    @property
    def n_trials(self) -> int:
        return self.response_hist.shape[0]
    
    @property
    def n_bins(self) -> int:
        return self.response_hist.shape[1]