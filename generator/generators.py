""" 
generators
==========

Response generator functions and classes. 

Use:
----

# simulation parameters
baseline_fr  = 40
response_fr  = 0
latency      = 0.350
duration     = 1.
baseline_T   = 2
stimulus_T   = 2
dt           = 0.001
induce_refractory_period = True
a            = 1.6
b            = 1.8

n_trials = 30

# initialize generator with the variables
generator = PoissonSpikeGenerator(
    baseline_fr=baseline_fr,
    response_fr=response_fr,
    latency=latency,
    duration=duration,
    baseline_T=baseline_T,
    stimulus_T=stimulus_T,
    dt=dt,
    induce_refractory_period=induce_refractory_period,
    a=a,
    b=b,
)

# generate trials
trial_activity = generator.generate(n_trials)

"""
import sys

import numpy as np
from scipy.stats import beta

from config import default_seed

class PoissonSpikeGenerator:
    def __init__(self, baseline_fr, response_fr, 
                 latency, duration, dt, baseline_T, stimulus_T, 
                 induce_refractory_period=False, kappa=4, a=None, b=None, rng=None):
        self.baseline_fr = baseline_fr
        self.response_fr = response_fr
        self.latency = latency
        self.duration = duration
        self.dt = dt
        self.baseline_T = baseline_T
        self.stimulus_T = stimulus_T

        self.total_bins = int((baseline_T + stimulus_T) / dt)

        self.induce_refractory_period = induce_refractory_period
        self.kappa = kappa
        self.a = a
        self.b = b

        self.r_t = self._build_rate_function()
        self.p = self.r_t * dt # prob of a spike in each time bin as a function of the time-varying rate
        
        if rng is None: 
            self.rng = default_seed
        else:
            self.rng = rng

    def _build_rate_function(self):
        # set the baseline fr for all bins
        r_t = np.full(self.total_bins, float(self.baseline_fr))

        # overwrite the response period with the response FR
        response_onset = int(self.latency / self.dt) + int(self.baseline_T / self.dt)
        response_offset = int((self.latency / self.dt) + int(self.duration / self.dt)) + int(self.baseline_T / self.dt) 

        if self.a and self.b:
            x_ = np.linspace(0, 1, response_offset - response_onset)
            r_ = beta.pdf(x_, self.a, self.b)

            fr_response = self.response_fr - self.baseline_fr
            r_r = r_ * fr_response / np.max(r_) +  self.baseline_fr

            try:
                r_t[response_onset:response_offset] = r_r
            except ValueError:
                print(f"stimulus time ({self.stimulus_T}) can't accomodate the response duration ({self.duration}) and latency ({self.latency}).")
                sys.exit(1)

        else:       
            r_t[response_onset:response_offset] = self.response_fr

        return r_t
    
    def _force_renewal_process(self, spike_train):
        """
        Induce a refractory period by removing every k-th spike.
        This will results in a spike train with ISIs following a gamma pdf.
        """
        kappa = self.kappa
        if spike_train.size == 0:
            return spike_train
        keep = np.arange(kappa-1, spike_train.size, kappa)
        return spike_train[keep]


    def generate(self, n_trials: int = 1, squeeze: bool = True):
        """
        Generate Poisson spike trains.

        Parameters
        ----------
        n_trials : int, default=1
            Number of trials to generate.
        squeeze : bool, default=True
            If True and n_trials==1, return a single 1D numpy array.
            Otherwise, return a list of 1D numpy arrays.

        Returns
        -------
        spikes : np.ndarray or list[np.ndarray]
            Spike times (seconds). 1D array if squeeze and n_trials==1, else list.
        """
        dt = self.dt
        p = self.p

        if n_trials == 1:
            hits = self.rng.random(self.total_bins) <= p
            idx = np.flatnonzero(hits)
            spike_times = idx.astype(float) * dt
            if self.induce_refractory_period:
                spike_times = self._force_renewal_process(spike_times)
            return spike_times if squeeze else [spike_times]

        hits = self.rng.random(size=(n_trials, self.total_bins)) <= p
        trials: list[np.ndarray] = []
        for i in range(n_trials):
            idx = np.flatnonzero(hits[i])
            ti = idx.astype(float) * dt

            if self.induce_refractory_period:
                ti = self._force_renewal_process(ti)
                
            trials.append(ti)
        return trials
            