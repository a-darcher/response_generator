from response_stats.responses.response_tests.base import * 
from scipy.stats import ttest_ind

from response_stats.config import default_seed

class SurrogateTest(ResponseTest):
    kind = TestKind.SURROGATE
    
    def __init__(self, n_perms=1000, rng=None, **ttest_kwargs):
        super().__init__()

        self.n_perms = n_perms
        self.ttest_kwargs = ttest_kwargs

        if rng is None:
            self.rng = np.random.default_rng(default_seed)
        else:
            self.rng = rng        

        self.bin_width = 0.05 #ms

    def _smooth_bins(self):
        pass

    def _get_whole_trial_bins(self, data: ResponseData) -> np.array:
        baseline_T = data.cfg.baseline_T
        stimulus_T = data.cfg.stimulus_T

        return np.arange(0, baseline_T+stimulus_T+self.bin_width, self.bin_width)

    def _bin_whole_trials(self, data: ResponseData,) -> np.ndarray:
        bins = self._get_whole_trial_bins(data)
        hist = np.array([np.histogram(trial, bins)[0] for trial in data.cfg.trial_activity])
        return hist, bins

    def _generate_surrogate(self, trial_activity_hist):
        n_trials = trial_activity_hist.shape[0]
        shifts = self.rng.integers(1, high=trial_activity_hist.shape[1], size=n_trials, dtype=np.int64, )
        return [np.roll(trial_activity_hist[n], shifts[n]) for n in np.arange(n_trials)]

    def construct_surrogates(self, data: ResponseData) -> np.ndarray:
        trial_activity_hist, _ = self._bin_whole_trials(data)

        surrogates = np.zeros((self.n_perms, trial_activity_hist.shape[0], trial_activity_hist.shape[1]),
                              dtype=trial_activity_hist.dtype,)
        for perm in np.arange(self.n_perms):
            s = self._generate_surrogate(trial_activity_hist)
            surrogates[perm, :, :] = s
        return surrogates

    def construct_baseline(self):
        pass

    def binwise_test(self, baseline_hist, response_hist):
        
        n_bins = response_hist.shape[1]

        tstats = np.zeros(n_bins)
        for n in np.arange(n_bins):
            res = ttest_ind(response_hist[:,n], baseline_hist, **self.ttest_kwargs)
            tstats[n] = res.statistic

        return tstats
    
    def compute_empirical_tstat(self, data: ResponseData) -> float:
        baseline_hist = data.baseline_hist
        response_hist = data.response_hist

        binwise_tstats = self.binwise_test(baseline_hist, response_hist)
        return np.max(binwise_tstats)

    def permute_tstats(self, data: ResponseData, surrogates: np.ndarray) -> np.array:

        bins_whole_trial = self._get_whole_trial_bins(data)
        
        permuted_tstats = np.ones(self.n_perms)
        baseline_ind = np.where(bins_whole_trial == data.cfg.baseline_T)[0][0]
        
        for n, s in enumerate(surrogates):
            b_hist = s[:, 0:baseline_ind]
            r_hist = s[:, baseline_ind:] 
            assert b_hist.shape[1] + r_hist.shape[1] == len(bins_whole_trial) - 1

            b_1_second = np.sum(b_hist, axis=1)
            r_hist_Hz = r_hist / self.bin_width

            b_tstats = self.binwise_test(b_1_second, r_hist_Hz)
            permuted_tstats[n] = np.max(b_tstats)
        
        return permuted_tstats
    
    def compute_pvalues(self, data: ResponseData) -> float:
        # construct and store the surrogates 
        self.surrogates = self.construct_surrogates(data)

        # calculate the empirical t-stat
        self.empirical_t = self.compute_empirical_tstat(data)

        # calculate the permuted t-stats
        self.permuted_tstats = self.permute_tstats(data, self.surrogates)

        p_value = (np.sum(self.permuted_tstats >= self.empirical_t) + 1) / (self.n_perms + 1)
        return p_value
        
