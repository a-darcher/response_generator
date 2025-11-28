import sys
sys.path.append("/home/al/Documents/code/generate_responses/generator")

import numpy as np

from generator.responses.config import *


class ResponseDetector:
    def __init__(self, data: ResponseData, test: ResponseTest):
        self.data = data
        self.test = test
        self.pvals_binwise = np.ndarray | None = None
        self.direction_of_bin: np.ndarray | None = None

    def _direction_mask(self, stimulus_bin: np.ndarray, baseline_sum: np.ndarray) -> bool:
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
    
    def compute_min_pval(self) -> float: