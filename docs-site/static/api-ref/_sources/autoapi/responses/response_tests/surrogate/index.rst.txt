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

   Bases: :py:obj:`response_generator.responses.response_tests.base.ResponseTest`


   Helper class that provides a standard way to create an ABC using
   inheritance.


   .. py:attribute:: kind


   .. py:attribute:: n_perms
      :value: 1000



   .. py:attribute:: ttest_kwargs


   .. py:method:: construct_surrogates(data: response_generator.responses.response_tests.base.ResponseData) -> response_generator.responses.response_tests.base.np.ndarray


   .. py:method:: construct_baseline()


   .. py:method:: binwise_test(baseline_hist, response_hist)


   .. py:method:: compute_empirical_tstat(data: response_generator.responses.response_tests.base.ResponseData) -> float


   .. py:method:: permute_tstats(data: response_generator.responses.response_tests.base.ResponseData, surrogates: response_generator.responses.response_tests.base.np.ndarray) -> response_generator.responses.response_tests.base.np.array


   .. py:method:: compute_pvalues(data: response_generator.responses.response_tests.base.ResponseData) -> float


