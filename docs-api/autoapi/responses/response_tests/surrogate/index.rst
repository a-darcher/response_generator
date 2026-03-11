responses.response_tests.surrogate
==================================

.. py:module:: responses.response_tests.surrogate


Classes
-------

.. autoapisummary::

   responses.response_tests.surrogate.SurrogateTest


Module Contents
---------------

.. py:class:: SurrogateTest(n_perms=1000, rng=None, **ttest_kwargs)

   Bases: :py:obj:`ResponseTest`


   .. py:attribute:: kind


   .. py:attribute:: n_perms
      :value: 1000



   .. py:attribute:: ttest_kwargs


   .. py:method:: construct_surrogates(data: ResponseData) -> np.ndarray


   .. py:method:: construct_baseline()


   .. py:method:: binwise_test(baseline_hist, response_hist)


   .. py:method:: compute_empirical_tstat(data: ResponseData) -> float


   .. py:method:: permute_tstats(data: ResponseData, surrogates: np.ndarray) -> np.array


   .. py:method:: compute_pvalues(data: ResponseData) -> float


