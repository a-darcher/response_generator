import numpy as np

from scipy.stats import wilcoxon

class ResponseCriteria:
    def __init__(self, trial_activity, 
                 baseline_T, stimulus_T, stimulus_onset, bin_width, dt,
                 proportion_active=1/3, 
                 debug=False,
                 direction="positive",
                 multiple_correction="simes", 
                 interleave_response_bins=True,
                 smooth_response_bins=None, # better to do false, then have other optional args? 
                 test="wilcoxon", **kwargs
                 ):
        """
        Parameters
        ----------
        trial_activity : list of np.ndarray
            List of spike times per trial.
        baseline_T : float
            Duration of baseline period (s).
        stimulus_T : float
            Duration of stimulus period (s).
        bin_width : float
            Bin width for spike counts (s).
        dt : float
            Simulation time step (s).
        proportion_active : float
            Minimum fraction of active trials required to test.
        direction : str
            Expected response direction ("positive"/"negative").
        multiple_correction : str
            Multiple-comparison correction ("simes" or "none").
        """
        self.debug = debug

        self.trial_activity = trial_activity
    
        self.baseline_T = baseline_T
        self.stimulus_T = stimulus_T
        self.stimulus_onset = stimulus_onset
        self.bin_width = bin_width
        self.dt = dt
    
        self.direction = direction.lower()
        self.proportion_active = proportion_active
        self.multiple_correction = multiple_correction.lower()
        self.interleave_response_bins = interleave_response_bins

        self.baseline_hist = self.bin_baseline()
        self.response_hist = self.bin_spikes()
        
        self.test = test
        self.test_kwargs = kwargs

        # Will be populated by compute_pvalue()     
        self.pvals_binwise = None
        self.direction_of_bin = None

    def bin_baseline(self):
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
        # count spikes during entire baseline period, already in Hz
        baseline_bins = [self.stimulus_onset - self.baseline_T, self.stimulus_onset] 
        baseline_hist = np.array([np.histogram(trial, baseline_bins)[0] for trial in self.trial_activity]).ravel()
        
        if self.debug:
            assert sum(baseline_hist) == sum([sum(t <= 1) for t in self.trial_activity]), "Binned baseline spikes do not match number of baseline spikes."

        baseline_duration = baseline_bins[1] - baseline_bins[0]
        return baseline_hist * 1 / baseline_duration
    

    def _interleave_bins(self, bins_standard, hist_standard):
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
        
        bins_interleave = np.arange(self.stimulus_onset+(self.bin_width/2), (self.stimulus_onset + self.stimulus_T), self.bin_width)
        hist_interleave = np.array([np.histogram(trial, bins_interleave)[0] for trial in self.trial_activity])
        
        interleaved = np.zeros((len(self.trial_activity), len(bins_standard)+len(bins_interleave)-2), int)
        interleaved[:, ::2] = hist_standard
        interleaved[:, 1::2] = hist_interleave

        if self.debug:
            lower = self.stimulus_onset + self.bin_width/2
            upper = self.stimulus_onset + self.stimulus_T - self.bin_width/2
            assert (hist_interleave).sum() == sum([sum((t >= lower) & (t <= upper)) for t in self.trial_activity]), "Binned stimulus spikes (interleaved period) do not match number of total stimulus spikes."
            assert interleaved.sum() == hist_interleave.sum() + hist_standard.sum(), "Interleaved matrix does not included the expected number of spikes."

        return interleaved
    
    def bin_spikes(self):
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
        bins = np.arange(self.stimulus_onset + self.dt, (self.stimulus_onset + self.stimulus_T)+self.bin_width, self.bin_width) 
        hist = np.array([np.histogram(trial, bins)[0] for trial in self.trial_activity])
        
        if self.debug:
            assert hist.sum() == sum([sum(t > 1) for t in self.trial_activity]), "Binned stimulus spikes (full period) do not match number of total stimulus spikes."

        if self.interleave_response_bins:
            binned_spikes = self._interleave_bins(bins, hist)
        else:
            binned_spikes = hist
        
        # convert to rate per second, from rate per (bin width)
        return binned_spikes * 1 / self.bin_width 
    
   

    def _resolve_test(self):


    def compute_pval(self):
        """
        Compute per-bin Wilcoxon tests against baseline, apply correction,
        and return minimum absolute p-value across bins.

        Returns
        -------
        min_pval : float
            Minimum absolute p-value across bins (after correction).
        """

        n_bins = self.response_hist.shape[1]
        n_trials = self.response_hist.shape[0]

        atrials = self.response_hist.any(1).sum()

        pvals_binwise = np.ones(n_bins)
        direction_of_bin = np.zeros(n_bins, dtype=bool)

        baseline_hist = self.baseline_hist

        # count number of spikes in baseline for determining response direction
        baseline_sum = baseline_hist.sum()

        if atrials > n_trials * self.proportion_active:
            for bin_i in range(n_bins):
                if (baseline_hist - self.response_hist[:, bin_i]).any():

                    _, pval = wilcoxon(self.response_hist[:, bin_i], baseline_hist)
                
                elif not (baseline_hist - self.response_hist[:, bin_i]).any():
                    pval = -1
                
                direction_of_bin[bin_i] = self._apply_direction_filter(self.response_hist[:, bin_i], baseline_sum)

                pvals_binwise[bin_i] = pval

            # restrict response search based on the direction of the response
            # by forcing bins with conflicting direction to have a value of 1.
            pvals_binwise[~direction_of_bin] = 1
            
            pvals_binwise = self._apply_multiple_correction(pvals_binwise)
        
        self.pvals_binwise = pvals_binwise
        self.direction_of_bin = direction_of_bin

        pval_abs = np.abs(pvals_binwise)
        return pval_abs.min()
        