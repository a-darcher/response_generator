responses.detector
==================

.. py:module:: responses.detector


Classes
-------

.. autoapisummary::

   responses.detector.ResponseDetector


Module Contents
---------------

.. py:class:: ResponseDetector(data: response_generator.responses.config.ResponseData, test_cls: type[response_generator.responses.response_tests.ResponseTest], **test_kwargs)

   .. py:attribute:: data


   .. py:attribute:: test


   .. py:attribute:: pvals_binwise
      :type:  numpy.ndarray | None
      :value: None



   .. py:attribute:: direction_of_bin
      :type:  numpy.ndarray | None
      :value: None



   .. py:method:: compute_min_pval() -> float

      Isolate the binwise pvalue evalutation.



