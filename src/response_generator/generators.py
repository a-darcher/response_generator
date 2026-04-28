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
import warnings
warnings.filterwarnings("error", category=RuntimeWarning)

import numpy as np
from scipy.stats import beta

from response_generator.config import default_seed

class PoissonSpikeGenerator:
    def __init__(self, baseline_fr, response_fr, 
                 latency, duration, dt, baseline_T, stimulus_T, 
                 induce_refractory_period=False, kappa=4, a=None, b=None, 
                 #
                 include_bursts=None, 
                 burst_rate_baseline=None, 
                 burst_rate_factor=None,
                 burst_rate_response=None, 
                 burst_response_time_factor=None, 
                 burst_duration_lam=None,
                 burst_alpha=None, burst_beta=None, 
                 burst_multiplier=None,
                 #
                 rng=None,
                 #
                 debug=None,):
        
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

        ## burst params
        self.include_bursts = include_bursts
        
        self.burst_rate_baseline = burst_rate_baseline
        self.burst_rate_factor   = burst_rate_factor
        self.burst_rate_response = self._handle_burst_rate_response(burst_rate_response)
        self.burst_duration_lam  = burst_duration_lam
        self.burst_response_time_factor = burst_response_time_factor
        self.burst_alpha         = burst_alpha
        self.burst_beta          = burst_beta
        self.burst_multiplier_baseline    = burst_multiplier
        self.burst_multiplier_response    = self._handle_burst_multiplier_response()
        if induce_refractory_period:
            self._initialize_burn_in()

        self.r_t = self._build_rate_function(self.total_bins, self.baseline_T)
        
        if rng is None: 
            self.rng = np.random.default_rng(default_seed)
        else:
            self.rng = rng

        if debug:
            self.debug = True
            self.burst_r_t_collection = []
        else:
            self.debug = False

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
    
    def _burn_in_period(self):
        burn_in = round(self.kappa / self.baseline_fr, 3)
        #print(burn_in)
        # if burn_in < 0.5:
        #     burn_in = 0.5
        return burn_in
    
    def _initialize_burn_in(self):
        # adjust FR to account for thinning process
        self.baseline_fr = self.baseline_fr * self.kappa
        self.response_fr = self.response_fr * self.kappa

        self.burn_in_period = self._burn_in_period()
        self.burn_in_baseline_T = self.baseline_T + self.burn_in_period
        self.burn_in_total_bins = int((self.burn_in_period + self.baseline_T + self.stimulus_T) / self.dt)
        self.burn_in_r_t = self._build_rate_function(self.burn_in_total_bins, self.burn_in_baseline_T)

        # return original FR values, mainly for plotting text
        self.baseline_fr = self.baseline_fr / self.kappa
        self.response_fr = self.response_fr / self.kappa

    def _build_rate_function(self, total_bins, baseline_T):
        # set the baseline fr for all bins
        r_t = np.full(total_bins, float(self.baseline_fr))

        # overwrite the response period with the response FR
        self.response_onset = int(self.latency / self.dt) + int(baseline_T / self.dt)
        self.response_offset = int((self.latency / self.dt) + int(self.duration / self.dt)) + int(baseline_T / self.dt) 
        if self.a and self.b:
            x_ = np.linspace(0, 1, self.response_offset - self.response_onset)
            r_ = beta.pdf(x_, self.a, self.b)

            fr_response = self.response_fr - self.baseline_fr
            r_r = r_ * fr_response / np.max(r_) +  self.baseline_fr

            try:
                r_t[self.response_onset:self.response_offset] = r_r
            except ValueError:
                print(f"stimulus time ({self.stimulus_T}) can't accomodate the response duration ({self.duration}) and latency ({self.latency}).")
                sys.exit(1)
        else:       
            r_t[self.response_onset:self.response_offset] = self.response_fr

        return r_t

    def _remove_burn_in_period(self, spike_times):
        spike_times = spike_times[spike_times > self.burn_in_period]
        spike_times = spike_times - self.burn_in_period
        return spike_times
    
    def _handle_burst_rate_response(self, burst_rate_response):
        # ensure that burst rate is lowered for negative responses
        if not self.include_bursts:
            return None
        else: 
            pass

        if self.response_fr < self.baseline_fr:
            burst_rate_response = 0
        elif np.isclose(self.response_fr, self.baseline_fr, atol=0.01):
            burst_rate_response = self.burst_rate_baseline
        else:
            burst_rate_response = burst_rate_response + (self.burst_rate_factor * self.response_fr) # R_r = r + 0.25FR_r 

        return burst_rate_response
    
    def _handle_burst_multiplier_response(self, ):
        if not self.include_bursts:
            return None
        else:
            pass

        if self.response_fr < self.baseline_fr:
            burst_multiplier_response = 0
        elif np.isclose(self.response_fr, self.baseline_fr, atol=0.01):
            burst_multiplier_response = self.burst_multiplier_baseline
        else:
            burst_multiplier_response = np.max([self.burst_multiplier_baseline, self.baseline_fr, self.response_fr])
        return burst_multiplier_response

    def induce_bursts(self, r_t, T_on, T_off, average_burst_rate, trial_section):

        segment_len = T_off - T_on
        n_bursts = self.rng.poisson(lam=average_burst_rate * segment_len, size=1)[0]

        burst_onsets = np.sort(self.rng.uniform(low=T_on, high=T_off, size=n_bursts))
        burst_onsets_ms = np.array(burst_onsets / self.dt, dtype=int)

        burst_duration = np.array(self.rng.normal(self.burst_duration_lam, self.burst_duration_lam / 4, size=n_bursts), dtype=int) # ms
        burst_duration = np.abs(burst_duration)

        # make minimum burst duration 3 ms to prevent div by 0 in Beta pdf normalization
        burst_duration = np.clip(burst_duration, 3, None)

        for b in range(n_bursts):   
            x_ = np.linspace(0, 1, burst_duration[b])
            r_ = beta.pdf(x_, self.burst_alpha, self.burst_beta)
            
            r_ = r_ / max(r_)

            if trial_section == "response":
                r_r = r_ * (self.burst_multiplier_response)
                r_r = r_r / (b+1)

                ind = burst_onsets_ms[b]
                base = self.r_t[ind]
                r_r = r_r + base 
            elif trial_section == "baseline":
                r_r = r_ * (self.burst_multiplier_baseline)
                base = self.baseline_fr
                r_r = r_r + self.baseline_fr 

            end_burst = np.min([burst_onsets_ms[b]+burst_duration[b], (T_off / self.dt)],)
            end_burst = int(end_burst)
            burst_len = end_burst - burst_onsets_ms[b]

            r_t[burst_onsets_ms[b]: end_burst] = r_r[:burst_len]
        
        return r_t
    
    def thin_indices(self, trial_activity, mean_fr, bin_centers, T_on, T_off, gt_mean, n_trials,):
        """Randomly thin spikes from a given section of the PSTH to match the ground truth 
        firing rate.

        Args:
            trial_activity (_type_): _description_
            mean_fr (_type_): _description_
            bin_centers (_type_): _description_
            T_on (_type_): _description_
            T_off (_type_): _description_
            gt_mean (_type_): _description_
            n_trials (_type_): _description_

        Returns:
            _type_: _description_
        """
        mean_fr_section = mean_fr[(bin_centers > T_on) & (bin_centers < T_off)]        
        fr_diff = np.mean(mean_fr_section) - gt_mean
        discrepancy_spikes = int(fr_diff * (T_off - T_on) * n_trials)
        ####
        #discrepancy_spikes = diff_spike_count + np.array(self.rng.normal(0, 0.5, 1) * gt_mean, dtype=int)[0]

        if discrepancy_spikes <= 0:
            return np.empty((0, 2))

        response_spikes = []
        for i, t in enumerate(trial_activity):
            r_spikes = (t > T_on) & (t < T_off)
            spikes_inds = np.flatnonzero(r_spikes)
            trial_inds = np.ones(len(spikes_inds)) * i
            response_spikes.extend(list(zip(trial_inds, spikes_inds)))

        ####
        # control for instances where the number of discrepant spikes (as calculated
        # based on the estimated firing rate) is greater than the number of response
        # spikes actually generated. 
        if discrepancy_spikes > len(response_spikes):
            return np.empty((0, 2))
        
        thin_ind = self.rng.choice(response_spikes, size=discrepancy_spikes, replace=False, )
        return thin_ind.astype(int)

    def correct_bursts_to_target_firing_rates(self, trial_activity, n_trials, bin_size):
        """
        Restore the simulated firing rates to the input/target firing rates,
        Calculates the discrepancy in the number of spikes between the ground-truth 
        rate function and the measured mean firing rate. 
        Thins spikes randomly within each baseline and response portion of the 
        psth, across trials. 
        To introduce some variation, the number of discrepant spikes are jittered
        by an amount sampled from a normal gaussian and scaled by the ground truth rate.

        Args:
            trial_activity (_type_): _description_
            n_trials (_type_): _description_
            bin_size (_type_): _description_

        Returns:
            _type_: _description_
        """
        # 
        bins = np.arange(0, self.baseline_T + self.stimulus_T + (bin_size), bin_size)
        bin_centers = np.convolve(bins, np.ones(2) / 2, mode="valid")
        binned_spikes = np.array([np.histogram(e, bins=bins)[0] for e in trial_activity]) / bin_size
        mean_fr = np.mean(binned_spikes, axis=0)

        gt_response_period_mean = np.mean(self.r_t[self.response_onset:self.response_offset])
        gt_baseline_one_mean = np.mean(self.r_t[0:self.response_onset])
        gt_baseline_two_mean = np.mean(self.r_t[self.response_offset:])

        # thin baseline 1
        T_on = 0
        T_off = self.response_onset / 1000
        thin_inds_b1 = self.thin_indices(trial_activity, mean_fr, bin_centers, T_on, T_off, gt_baseline_one_mean, n_trials)

        # response
        T_on = self.response_onset / 1000
        T_off = self.response_offset / 1000
        thin_inds_r = self.thin_indices(trial_activity, mean_fr, bin_centers, T_on, T_off, gt_response_period_mean, n_trials)

        # baseline 2 
        T_on = self.response_offset / 1000
        T_off = self.baseline_T + self.stimulus_T
        thin_inds_b2 = self.thin_indices(trial_activity, mean_fr, bin_centers, T_on, T_off, gt_baseline_two_mean, n_trials)

        thin_ind = np.concatenate([thin_inds_b1, thin_inds_r, thin_inds_b2])

        remove_by_col = {}
        for r, c in thin_ind:
            remove_by_col.setdefault(r, set()).add(c)

        data= [
            row[[j for j in range(len(row)) if j not in remove_by_col.get(i, set())]]
            for i, row in enumerate(trial_activity)
            ]
        
        return data

    def generate_with_bursts(self, n_trials: int = 2, bin_size=25/1000):
        """TODO: speed this up like 100000x

        Args:
            n_trials (int, optional): _description_. Defaults to 2.
            bin_size (_type_, optional): _description_. Defaults to 25/1000.

        Returns:
            _type_: _description_
        """
        dt = self.dt

        trials: list[np.ndarray] = []
        for i in range(n_trials):
            r_t = self.r_t.copy()

            if self.baseline_fr == self.response_fr:
                T_on = 0
                T_off = (self.baseline_T + self.stimulus_T)
                r_t = self.induce_bursts(r_t, T_on, T_off, self.burst_rate_baseline, trial_section="baseline")
            
            else:
                T_on = 0
                T_off = (self.response_onset * dt)
                r_t = self.induce_bursts(r_t, T_on, T_off, self.burst_rate_baseline, trial_section="baseline")

                T_on = (self.response_onset * dt)
                T_off = (self.response_offset * dt) 
                r_t = self.induce_bursts(r_t, T_on, T_off, self.burst_rate_response, trial_section="response")

                T_on = self.response_offset * dt
                T_off = (self.baseline_T + self.stimulus_T)
                r_t = self.induce_bursts(r_t, T_on, T_off, self.burst_rate_baseline, trial_section="baseline")
                
            if self.debug:
                self.burst_r_t_collection.append(r_t)

            p = r_t * dt 
            u = self.rng.random(self.total_bins) 
            idx = np.flatnonzero(u <= p)
            spike_times = idx.astype(float) * dt

            # remove the "right-hand" spikes corresponding to the 10th percentile of the ISIs
            isis = np.diff(spike_times)
            percentile = 0.1
            if isis.size > 1:
                k = max(0, int(percentile * isis.size) - 1)
                thr = np.partition(isis, k)[k] # cheaper sorting to get percentile boundary
                bad = np.flatnonzero(isis <= thr) + 1 # get the index of the right hand side spike
                keep = np.ones(spike_times.size, dtype=bool) # make a mask 
                keep[bad] = False
                spike_times = spike_times[keep] # filter with mask
            trials.append(spike_times)

        trials = self.correct_bursts_to_target_firing_rates(trials, n_trials, bin_size)

        return trials

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
    
        if self.include_bursts: 
            return self.generate_with_bursts(n_trials,) 
    
        dt = self.dt
        if self.induce_refractory_period:
            total_bins = self.burn_in_total_bins
            r_t = self.burn_in_r_t
        else:
            total_bins = self.total_bins
            r_t = self.r_t
        
        p = r_t * dt # prob of a spike in each time bin as a function of the time-varying rate

        if n_trials == 1:
            hits = self.rng.random(total_bins) <= p
            idx = np.flatnonzero(hits)
            spike_times = idx.astype(float) * dt

            if self.induce_refractory_period:
                spike_times = self._force_renewal_process(spike_times)
                spike_times = self._remove_burn_in_period(spike_times)

            return spike_times if squeeze else [spike_times]

        hits = self.rng.random(size=(n_trials, total_bins)) <= p
        trials: list[np.ndarray] = []
        for i in range(n_trials):
            idx = np.flatnonzero(hits[i])
            spike_times = idx.astype(float) * dt

            if self.induce_refractory_period:
                spike_times = self._force_renewal_process(spike_times)
                spike_times = self._remove_burn_in_period(spike_times)
                
            trials.append(spike_times)

        return trials
    
