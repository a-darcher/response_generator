import numpy as np
import numba as nb
from scipy.stats import beta

@nb.njit
def _force_renewal_process_numba(spike_train, kappa):
    if spike_train.size == 0:
            return spike_train
    return spike_train[kappa-1::kappa]

@nb.njit
def _generate_trials_numba(r_t, dt, n_trials, induce_refractory, kappa):
    total_bins = r_t.size
    trials = []

    for trial in range(n_trials):
        hits = np.random.rand(total_bins) <= (r_t * dt)
        spike_times = np.nonzero(hits)[0].astype(np.float64) * dt

        if induce_refractory:
            spike_times = _force_renewal_process_numba(spike_times, kappa)
        
        trials.append(spike_times)
    
    return trials

from scipy.ndimage import gaussian_filter

class PoissonSpikeGenerator:
    def __init__(self, baseline_fr, response_fr, 
                 latency, duration, dt, baseline_T, stimulus_T, 
                 induce_refractory_period=False, kappa=4, a=None, b=None):
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
            r_t[response_onset:response_offset] = r_r

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
            hits = np.random.rand(self.total_bins) <= p
            idx = np.flatnonzero(hits)
            spike_times = idx.astype(float) * dt
            if self.induce_refractory_period:
                spike_times = self._force_renewal_process(spike_times)
            return spike_times if squeeze else [spike_times]

        hits = np.random.rand(n_trials, self.total_bins) <= p
        trials: list[np.ndarray] = []
        for i in range(n_trials):
            idx = np.flatnonzero(hits[i])
            ti = idx.astype(float) * dt

            if self.induce_refractory_period:
                ti = self._force_renewal_process(ti)
                
            trials.append(ti)
        return trials
            
    def generate_numba(self, n_trials: int = 1, squeeze: bool = True):
        spikes = _generate_trials_numba(
            self.r_t, self.dt, n_trials,
            self.induce_refractory_period, self.kappa
        )
        if n_trials == 1 and squeeze:
            return spikes[0]
        return spikes

    # def generate_trial(self):

    #     spike_train = []
        
    #     t = 0
    #     while t < (self.baseline_T + self.stimulus_T) / self.dt:
    #         x_i = np.random.random()
    #         r_i = self.r_t[t]

    #         if x_i <= r_i * self.dt:
    #             spike_train.append(t * self.dt)
    #         t += 1

    #     if self.induce_refractory_period:
    #         spike_train = self._force_renewal_process(np.array(spike_train), self.kappa)

    #     return np.array(spike_train)
    
    # def generate_trials(self, n_trials):
    #     return [self.generate_trial() for _ in range(n_trials)]

