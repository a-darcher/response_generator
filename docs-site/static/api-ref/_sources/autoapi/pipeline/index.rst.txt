pipeline
========

.. py:module:: pipeline

.. autoapi-nested-parse::

   pipeline.py — simulate a set of responses using parameters from a config file.

   Author: Alana Darcher
   Email: darcher@tuta.io
   Date: 2025-Nov-27

   Example Usage:
   $ python3 pipeline.py --config configs/test.yaml



Attributes
----------

.. autoapisummary::

   pipeline.Sampler
   pipeline.ResponseMethod


Classes
-------

.. autoapisummary::

   pipeline.SimulationConfig
   pipeline.ResponseSimulator


Functions
---------

.. autoapisummary::

   pipeline.run
   pipeline.main


Module Contents
---------------

.. py:data:: Sampler

.. py:data:: ResponseMethod

.. py:class:: SimulationConfig

   .. py:attribute:: n_samples
      :type:  int


   .. py:attribute:: save_dir
      :type:  pathlib.Path


   .. py:attribute:: save_language
      :type:  str


   .. py:attribute:: response_type
      :type:  str


   .. py:attribute:: trial_range
      :type:  int | tuple | list


   .. py:attribute:: baseline_T
      :type:  float


   .. py:attribute:: stimulus_T
      :type:  float


   .. py:attribute:: dt
      :type:  float


   .. py:attribute:: beta_a_range
      :type:  tuple | list


   .. py:attribute:: beta_multiplier_range
      :type:  tuple | list


   .. py:attribute:: duration_range
      :type:  float | tuple | list


   .. py:attribute:: latency_range
      :type:  float | tuple | list


   .. py:attribute:: induce_refractory_period
      :type:  bool


   .. py:attribute:: include_bursts
      :type:  bool
      :value: False



   .. py:attribute:: burst_rate_baseline
      :type:  float | bool
      :value: False



   .. py:attribute:: burst_rate_factor
      :type:  float | bool
      :value: False



   .. py:attribute:: burst_rate_response
      :type:  float | bool
      :value: False



   .. py:attribute:: burst_rate_baseline_scale
      :type:  float | bool
      :value: False



   .. py:attribute:: burst_rate_response_scale
      :type:  float | bool
      :value: False



   .. py:attribute:: burst_duration_lam
      :type:  float | bool
      :value: False



   .. py:attribute:: burst_response_time_factor
      :type:  float | bool
      :value: False



   .. py:attribute:: burst_alpha
      :type:  float | bool
      :value: False



   .. py:attribute:: burst_beta
      :type:  float | bool
      :value: False



   .. py:attribute:: burst_multiplier
      :type:  float | bool
      :value: False



   .. py:attribute:: generate_supplementary_trials
      :type:  bool
      :value: False



   .. py:attribute:: supplementary_default_count
      :type:  int | bool
      :value: False



   .. py:attribute:: seed
      :type:  int
      :value: 73



   .. py:attribute:: baseline_threshold
      :type:  int | bool
      :value: False



   .. py:attribute:: baseline_scale
      :type:  int | bool
      :value: False



   .. py:attribute:: baseline_range
      :type:  tuple | list | bool
      :value: False



   .. py:attribute:: response_fr_sampler
      :type:  Sampler
      :value: 'uniform'



   .. py:attribute:: response_fr_method
      :type:  ResponseMethod
      :value: 'linear_function'



   .. py:attribute:: response_fr_scale
      :type:  float
      :value: 2



   .. py:attribute:: response_fr_max
      :type:  float | bool
      :value: False



   .. py:attribute:: gain_response_fixed
      :type:  float | bool
      :value: False



   .. py:attribute:: gain_response_y
      :type:  float | bool
      :value: False



   .. py:attribute:: gain_response_high
      :type:  float | bool
      :value: False



   .. py:attribute:: gain_response_e
      :type:  float | bool
      :value: False



   .. py:attribute:: linear_response_slope
      :type:  float | bool
      :value: False



   .. py:attribute:: linear_response_offset
      :type:  float | bool
      :value: False



   .. py:method:: from_yaml(path: pathlib.Path) -> SimulationConfig
      :staticmethod:


      Construct a SimulationConfig dataclass from a config file.

      :param path: path to the config file
      :type path: Path

      :returns: dataclass instance
      :rtype: SimulationConfig



.. py:class:: ResponseSimulator(cfg: SimulationConfig)

   .. py:attribute:: cfg


   .. py:attribute:: rng


   .. py:attribute:: time_str


   .. py:attribute:: dir_name


   .. py:attribute:: save_dir


   .. py:method:: run() -> pandas.DataFrame

      Runner for simulating the specified batch of units.

      :returns: collection of simulating trial-wise activity and collected parameters
      :rtype: pd.DataFrame



.. py:function:: run(config: SimulationConfig) -> pandas.DataFrame

.. py:function:: main(argv=None)

