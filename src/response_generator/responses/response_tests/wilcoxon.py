from response_generator.responses.response_tests.base import *
from scipy.stats import wilcoxon

class WilcoxonTest(ResponseTest):
    kind = TestKind.PARAMETRIC
    
    def __init__(self, **wilcoxon_kwargs):
        super().__init__()
        self.wilcoxon_kwargs = wilcoxon_kwargs

    def compute_pvalues(self, data: ResponseData) -> np.ndarray:
        n_bins = data.n_bins
        pvals = np.ones(n_bins)
        baseline = data.baseline_hist

        for i in range(n_bins):
            stim_bin = data.response_hist[:, i]
            if (baseline - stim_bin).any():
                _, p = wilcoxon(stim_bin, baseline, **self.wilcoxon_kwargs)
                pvals[i] = p
            else:
                pvals[i] = -1.0   

        return pvals