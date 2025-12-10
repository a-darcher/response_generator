import numpy as np

from response_stats.responses.config import ResponseData
from response_stats.responses.response_tests import ResponseTest, TestKind

class ResponseDetector:
    def __init__(self, data: ResponseData, test_cls: type[ResponseTest]):
        self.data = data
        self.test = test_cls()
        self.pvals_binwise: np.ndarray | None = None
        self.direction_of_bin: np.ndarray | None = None

    def _direction_mask(self, raw_pvalues: np.ndarray,) -> bool:
            """
            Mask pvalues by direction.
            For 'positive', total spikes in the bin >= baseline_sum.
            For 'negative', total spikes in the bin  < baseline_sum.
            """
            ## TODO -- really think about if comparing the response bin sum to the
            ## baseline total sum is better than taking and comparing an average ...
            baseline_sum = self.data.baseline_hist.sum()
            response_sums_binwise = np.sum(self.data.response_hist, axis=0)

            if self.data.cfg.direction == "positive":
                mask = response_sums_binwise >= baseline_sum
                raw_pvalues[~mask] = 1
            
            elif self.data.cfg.direction == "negative":
                mask = response_sums_binwise <= baseline_sum
                raw_pvalues[~mask] = 1

            elif self.data.cfg.direction == "none":
                pass
            
            else:
                raise ValueError(f"Direction of response ({self.data.cfg.direction!r}) not recognized.")
        
            return raw_pvalues
    
    def _multiple_correction(self, pvals_binwise, *, method: str | None = None,
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
        method = (method or self.data.cfg.multiple_correction).lower()

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
    
    def compute_min_pval(self) -> float:
        """
        Isolate the binwise pvalue evalutation. 
        """
        cfg = self.data.cfg
        response_hist = self.data.response_hist

        n_trials = response_hist.shape[0]
        n_bins = response_hist.shape[1]

        pvals_binwise = np.ones(n_bins)

        atrials = response_hist.any(1).sum()
        if atrials > n_trials * cfg.proportion_active:
            raw_pvalues = self.test.compute_pvalues(self.data)

        if self.test.kind is TestKind.PARAMETRIC:    
            pvals_binwise = self._direction_mask(raw_pvalues)
            pvals_binwise = self._multiple_correction(pvals_binwise)
            pval_abs = np.abs(pvals_binwise)
            pval = pval_abs.min()
        elif self.test.kind is TestKind.SURROGATE:
            # output of surrogate is the direct pvalue
            pval = raw_pvalues
        
        return pval