responses.binning
=================

.. py:module:: responses.binning


Functions
---------

.. autoapisummary::

   responses.binning.bin_baseline
   responses.binning.bin_spikes
   responses.binning.make_response_data


Module Contents
---------------

.. py:function:: bin_baseline(cfg: response_stats.responses.config.ResponseConfig) -> numpy.ndarray

   Treats the entire baseline period as a single bin
   and returns the spike count during this bin, scaled to Hz.

   Notes:
   - could generalize this to enable finer-grained binning.

   :returns: **baseline_hist** -- Spike counts in baseline per trial.
   :rtype: np.ndarray, shape (n_trials,)


.. py:function:: bin_spikes(cfg: response_stats.responses.config.ResponseConfig)

   Bin spikes during the stimulus period.
   Can optionally interleave the bins by setting `interleave_response_bins` to True in the class initialization.
   See _interleave_bins() for details.

   Scales the spike counts to Hz.
   Spikes with times exactly equal to the stimulus onset are not included, and are counted by the baseline period.

   :returns: **np.ndarray**
   :rtype: shape (n_trials, n_bins) spike counts (Hz).


.. py:function:: make_response_data(cfg: response_stats.responses.config.ResponseConfig) -> response_stats.responses.config.ResponseData

