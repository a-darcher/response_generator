plot_utils
==========

.. py:module:: plot_utils

.. autoapi-nested-parse::

   plot_utils
   ==========

   Create summary visualizations of a generated response.

   Use:
   ----
   n_trials = 10

   generator = PoissonSpikeGenerator(...)
   trial_activity = generator.generate(n_trials)
   criteria = ResponseCriteria(...)

   params = grab_fields(generator, criteria, n_trials)
   fig = SpikeSummaryFigure(trial_activity, generator, criteria, params)
   fig.build()
   plt.show()



Classes
-------

.. autoapisummary::

   plot_utils.SpikePlotParams
   plot_utils.SpikeSummaryFigure


Functions
---------

.. autoapisummary::

   plot_utils.grab_fields


Module Contents
---------------

.. py:class:: SpikePlotParams

   .. py:attribute:: n_trials
      :type:  int


   .. py:attribute:: baseline_fr
      :type:  float


   .. py:attribute:: response_fr
      :type:  float


   .. py:attribute:: latency
      :type:  float


   .. py:attribute:: duration
      :type:  float


   .. py:attribute:: baseline_T
      :type:  float


   .. py:attribute:: stimulus_T
      :type:  float


   .. py:attribute:: dt
      :type:  float


   .. py:attribute:: bin_width
      :type:  float


   .. py:attribute:: induce_refractory_period
      :type:  bool


   .. py:attribute:: a
      :type:  float


   .. py:attribute:: b
      :type:  float


   .. py:attribute:: direction
      :type:  str


   .. py:attribute:: multiple_correction
      :type:  str


   .. py:attribute:: baseline_T_stat
      :type:  float


   .. py:attribute:: proportion_active
      :type:  float


.. py:function:: grab_fields(generator, detector, n_trials)

.. py:class:: SpikeSummaryFigure(trial_activity, generator, detector)

   .. py:attribute:: trial_activity


   .. py:attribute:: generator


   .. py:attribute:: detector


   .. py:attribute:: params


   .. py:attribute:: fig
      :value: None



   .. py:attribute:: axes
      :value: None



   .. py:method:: build(figsize=(6, 4), constrained=True)


