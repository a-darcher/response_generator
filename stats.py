import numpy as np
import numba as nb
from numba.typed import List

from scipy.stats import mannwhitneyu, wilcoxon

class ResponseCriteria:
    def __init__(self, trial_activity, baseline_T, stimulus_T, bin_width, dt,
                 proportion_active=1/3, direction="positive",
                 multiple_correction="simes", 
                 debug=False):
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
        self.bin_width = bin_width
        self.dt = dt
    
        self.direction = direction.lower()
        self.proportion_active = proportion_active
        self.multiple_correction = multiple_correction.lower()

        self.baseline_hist = self.bin_baseline()
        self.interleaved = self.bin_spikes()
        
        # Will be populated by compute_pvalue()     
        self.pvals_binwise = None
        self.direction_of_bin = None

    def bin_baseline(self):
        """
        Bin spikes across the baseline period into a single count per trial.

        Returns
        -------
        baseline_hist : np.ndarray, shape (n_trials,)
            Spike counts in baseline per trial.
        """
        baseline_bins = [0, self.baseline_T] # count spikes during entire baseline period, already in Hz
        baseline_hist = np.array([np.histogram(trial, baseline_bins)[0] for trial in self.trial_activity]).ravel()
        
        if self.debug:
            assert sum(baseline_hist) == sum([sum(t <= 1) for t in self.trial_activity]), "Binned baseline spikes do not match number of baseline spikes."

        return baseline_hist
    
    def bin_spikes(self):
        """
        Bin spikes during the stimulus period, using the interleaving method (bin twice: once using bins capped by the stimulus onset and offset with intervals of the given bin width, and 
        once using bins offset by half the bin width with caps of stimulus_onset + half bin width and stimulus_offset - half bin width. Alternate the bins for the final returned entry). 

        Scales the spike counts to Hz. 
        Will not count spikes with times exactly equal to the stimulus onset (these are assigned to the baseline period).
        The interleaved bins will count spike times exactly equal to (stimulus onset + half bin width) and (stimulus offset - half bin width). 

        Returns
        -------
        interleaved : np.ndarray, shape (n_trials, n_bins)
            Interleaved spike counts (Hz).
        """

        # note: onset of bins is baseline time + dt, to allow border-spikes to be counted only in the baseline
        bins_straight_up = np.arange(self.baseline_T + self.dt, (self.baseline_T + self.stimulus_T)+self.bin_width, self.bin_width) 
        bins_betweeners = np.arange(self.baseline_T+(self.bin_width/2), (self.baseline_T + self.stimulus_T), self.bin_width)

        # bin data, spike count / 100 ms
        hist_straight_up = np.array([np.histogram(trial, bins_straight_up)[0] for trial in self.trial_activity])
        hist_betweeners = np.array([np.histogram(trial, bins_betweeners)[0] for trial in self.trial_activity])

        if self.debug:
            assert hist_straight_up.sum() == sum([sum(t > 1) for t in self.trial_activity]), "Binned stimulus spikes (full period) do not match number of total stimulus spikes."
            lower = self.baseline_T + self.bin_width/2
            upper = self.baseline_T + self.stimulus_T - self.bin_width/2
            assert (hist_betweeners).sum() == sum([sum((t >= lower) & (t <= upper)) for t in self.trial_activity]), "Binned stimulus spikes (interleaved period) do not match number of total stimulus spikes."

        interleaved = np.zeros((len(self.trial_activity), len(bins_straight_up)+len(bins_betweeners)-2), int)
        interleaved[:, ::2] = hist_straight_up
        interleaved[:, 1::2] = hist_betweeners

        if self.debug:
            assert interleaved.sum() == hist_betweeners.sum() + hist_straight_up.sum(), "Interleaved matrix does not included the expected number of spikes."

        # convert to rate per second, from rate per (bin width)
        return interleaved * self.stimulus_T / self.bin_width
    
    def _apply_direction_filter(self, stimulus_bin: np.ndarray, baseline_sum: np.ndarray) -> bool:
        """
        Return True if this bin matches the expected response direction.
        For 'positive', total spikes in the bin >= baseline_sum.
        For 'negative', total spikes in the bin  < baseline_sum.
        """
        if self.direction == "positive":
            return stimulus_bin.sum() >= baseline_sum
        elif self.direction == "negative":
            return stimulus_bin.sum() < baseline_sum
        else:
            raise ValueError(f"Direction of response ({self.direction!r}) not recognized.")
    
    def _apply_multiple_correction(self, pvals_binwise, *, method: str | None = None,
                                   preserve_order: bool = False) -> np.ndarray:
        """
        Apply multiple-comparison correction to binwise p-values.

        Parameters
        ----------
        pvals_binwise : np.ndarray
            Array of p-values per bin.
        method : str | None
            If None, use self.multiple_correction. Options: 'simes', 'none'.
        preserve_order : bool
            If True, return adjusted p-values in original bin order.
            If False, return the sorted-and-adjusted array (OK if you only take min).

        Returns
        -------
        np.ndarray
            Adjusted p-values (order depends on preserve_order).
        """
        method = (method or self.multiple_correction).lower()

        if method == "none":
            return pvals_binwise

        if method == "simes":
            
            p = np.asarray(pvals_binwise, dtype=float)

            if preserve_order:
                order = np.argsort(p)
                ranks = np.empty_like(order)
                ranks[order] = np.arange(1, len(p), 1)
                adjusted = p * (len(p) / ranks)
                return adjusted
            else:
                p_sorted = np.sort(p)
                adjusted_sorted = p_sorted * (len(p_sorted) / np.arange(1, len(p_sorted) + 1))
                return adjusted_sorted

        raise ValueError(f"multiple_correction not recognized: {method!r}")


    def compute_pval(self):
        """
        Compute per-bin Wilcoxon tests against baseline, apply correction,
        and return minimum absolute p-value across bins.

        Returns
        -------
        min_pval : float
            Minimum absolute p-value across bins (after correction).
        """

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
                
                direction_of_bin[bin_i] = self._apply_direction_filter(self.interleaved[:, bin_i], baseline_sum)

                pvals_binwise[bin_i] = pval

            # restrict response search based on the direction of the response
            # by forcing bins with conflicting direction to have a value of 1.
            pvals_binwise[~direction_of_bin] = 1
            
            pvals_binwise = self._apply_multiple_correction(pvals_binwise)
        
        self.pvals_binwise = pvals_binwise
        self.direction_of_bin = direction_of_bin

        pval_abs = np.abs(pvals_binwise)
        return pval_abs.min()
        