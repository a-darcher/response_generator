responses.config
================

.. py:module:: responses.config

.. autoapi-nested-parse::

   config.py - dataclass objects for specify response search parameters

   Author: Alana Darcher
   Email: darcher@tuta.io
   Date: 2025-Nov-28



Attributes
----------

.. autoapisummary::

   responses.config.Direction
   responses.config.Correction


Classes
-------

.. autoapisummary::

   responses.config.ResponseConfig
   responses.config.ResponseData


Module Contents
---------------

.. py:data:: Direction

.. py:data:: Correction

.. py:class:: ResponseConfig

   .. py:attribute:: trial_activity
      :type:  list[numpy.ndarray]


   .. py:attribute:: baseline_T
      :type:  float


   .. py:attribute:: stimulus_T
      :type:  float


   .. py:attribute:: stimulus_onset
      :type:  int


   .. py:attribute:: bin_width
      :type:  float


   .. py:attribute:: dt
      :type:  float


   .. py:attribute:: direction
      :type:  Direction
      :value: 'positive'



   .. py:attribute:: proportion_active
      :type:  float
      :value: 0.3333333333333333



   .. py:attribute:: multiple_correction
      :type:  Correction
      :value: 'simes'



   .. py:attribute:: interleave_response_bins
      :type:  bool
      :value: True



   .. py:attribute:: smooth_response_bins
      :type:  None | bool
      :value: False



   .. py:attribute:: debug
      :type:  bool
      :value: False



.. py:class:: ResponseData

   .. py:attribute:: cfg
      :type:  ResponseConfig


   .. py:attribute:: baseline_hist
      :type:  numpy.ndarray


   .. py:attribute:: response_hist
      :type:  numpy.ndarray


   .. py:property:: n_trials
      :type: int



   .. py:property:: n_bins
      :type: int



