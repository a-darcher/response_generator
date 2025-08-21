import numpy as np
from scipy.stats import mannwhitneyu, wilcoxon


class ResponseCriteria:
    def __init__(self, trial_activity, baseline_T, stimulus_T, bin_width, dt,
                 proportion_active=1/3, direction="positive",
                 multiple_correction="simes"):
        
        self.trial_activity = trial_activity
    
        self.baseline_T = baseline_T
        self.stimulus_T = stimulus_T
        self.bin_width = bin_width
        self.dt = dt
    
        self.proportion_active = proportion_active
        self.multiple_correction = multiple_correction.lower()

        self.baseline_hist = self.bin_baseline()
        self.interleaved = self.bin_spikes()
        
        # Will be populated by compute_pvalue()
        
        self.pvals_binwise = None
        self.direction_of_bin = None



    def bin_baseline(self):
        baseline_bins = [0, self.baseline_T] # count spikes during entire baseline period, already in Hz
        baseline_hist = np.array([np.histogram(trial, baseline_bins)[0] for trial in self.trial_activity]).ravel()
        assert sum(baseline_hist) == sum([sum(t <= 1) for t in self.trial_activity]), "Binned baseline spikes do not match number of baseline spikes."

        return baseline_hist
    
    def bin_spikes(self):
        """Bin spikes during the stimulus period, using the interleaving method (bin twice: once using bins capped by the stimulus onset and offset with intervals of the given bin width, and 
        once using bins offset by half the bin width with caps of stimulus_onset + half bin width and stimulus_offset - half bin width. Alternate the bins for the final returned entry). 

        Scales the spike counts to Hz. 
        Will not count spikes with times exactly equal to the stimulus onset (these are assigned to the baseline period).
        The interleaved bins will count spike times exactly equal to (stimulus onset + half bin width) and (stimulus offset - half bin width). 

        Returns:
            _type_: _description_
        """

        # note: onset of bins is baseline time + dt, to allow border-spikes to be counted only in the baseline
        bins_straight_up = np.arange(self.baseline_T + self.dt, (self.baseline_T + self.stimulus_T)+self.bin_width, self.bin_width) 
        bins_betweeners = np.arange(self.baseline_T+(self.bin_width/2), (self.baseline_T + self.stimulus_T), self.bin_width)

        # bin data, spike count / 100 ms
        hist_straight_up = np.array([np.histogram(trial, bins_straight_up)[0] for trial in self.trial_activity])
        hist_betweeners = np.array([np.histogram(trial, bins_betweeners)[0] for trial in self.trial_activity])

        assert hist_straight_up.sum() == sum([sum(t > 1) for t in self.trial_activity]), "Binned stimulus spikes (full period) do not match number of total stimulus spikes."
        lower = self.baseline_T + self.bin_width/2
        upper = self.baseline_T + self.stimulus_T - self.bin_width/2
        assert (hist_betweeners).sum() == sum([sum((t >= lower) & (t <= upper)) for t in self.trial_activity]), "Binned stimulus spikes (interleaved period) do not match number of total stimulus spikes."

        interleaved = np.zeros((len(self.trial_activity), len(bins_straight_up)+len(bins_betweeners)-2), int)
        interleaved[:, ::2] = hist_straight_up
        interleaved[:, 1::2] = hist_betweeners
        assert interleaved.sum() == hist_betweeners.sum() + hist_straight_up.sum(), "Interleaved matrix does not included the expected number of spikes."

        # convert to rate per second, from rate per (bin width)
        return interleaved * self.stimulus_T / self.bin_width

    def compute_pval(self):

        n_bins = self.interleaved.shape[1]
        n_trials = self.interleaved.shape[0]

        atrials = self.interleaved.any(1).sum()

        pvals_binwise = np.ones(n_bins)
        direction_of_bin = np.zeros(n_bins, dtype=bool)

        # count number of spikes in baseline for determining response direction
        baseline_sum = self.baseline_hist.sum()

        if atrials > n_trials * self.proportion_active:
            
            
            for bin_i in range(n_bins):
                if (self.baseline_hist - self.interleaved[:, bin_i]).any():
                    _, pval = wilcoxon(self.interleaved[:, bin_i], self.baseline_hist)
                
                elif not (self.baseline_hist - self.interleaved[:, bin_i]).any():
                    pval = -1
                
                direction_of_bin[bin_i] = self.interleaved[:, bin_i].sum() >= baseline_sum

                pvals_binwise[bin_i] = pval

            # restrict response search based on the direction of the response
            # by forcing bins with conflicting direction to have a value of 1.
            pvals_binwise[~direction_of_bin] = 1
            
            # apply Simes 
            pvals_binwise.sort()
            pvals_binwise *=  n_bins / np.arange(1, n_bins + 1)

        pval_abs = np.abs(pvals_binwise)

        return pval_abs.min()
        