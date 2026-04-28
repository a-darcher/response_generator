responses.response_tests.wilcoxon
=================================

.. py:module:: responses.response_tests.wilcoxon


Classes
-------

.. autoapisummary::

   responses.response_tests.wilcoxon.WilcoxonTest


Module Contents
---------------

.. py:class:: WilcoxonTest(**wilcoxon_kwargs)

   Bases: :py:obj:`response_generator.responses.response_tests.base.ResponseTest`


   Helper class that provides a standard way to create an ABC using
   inheritance.


   .. py:attribute:: kind


   .. py:attribute:: wilcoxon_kwargs


   .. py:method:: compute_pvalues(data: response_generator.responses.response_tests.base.ResponseData) -> response_generator.responses.response_tests.base.np.ndarray


