generators
==========

.. py:module:: generators

.. autoapi-nested-parse::

   generators
   ==========

   Response generator functions and classes.

   Use:
   ----

   # simulation parameters
   baseline_fr  = 40
   response_fr  = 0
   latency      = 0.350
   duration     = 1.
   baseline_T   = 2
   stimulus_T   = 2
   dt           = 0.001
   induce_refractory_period = True
   a            = 1.6
   b            = 1.8

   n_trials = 30

   # initialize generator with the variables
   generator = PoissonSpikeGenerator(
       baseline_fr=baseline_fr,
       response_fr=response_fr,
       latency=latency,
       duration=duration,
       baseline_T=baseline_T,
       stimulus_T=stimulus_T,
       dt=dt,
       induce_refractory_period=induce_refractory_period,
       a=a,
       b=b,
   )

   # generate trials
   trial_activity = generator.generate(n_trials)



Classes
-------

.. autoapisummary::

   generators.PoissonSpikeGenerator


Module Contents
---------------

.. py:class:: PoissonSpikeGenerator(baseline_fr, response_fr, latency, duration, dt, baseline_T, stimulus_T, induce_refractory_period=False, kappa=4, a=None, b=None, include_bursts=None, burst_rate_baseline=None, burst_rate_factor=None, burst_rate_response=None, burst_response_time_factor=None, burst_duration_lam=None, burst_alpha=None, burst_beta=None, burst_multiplier=None, rng=None, debug=None)

   .. py:attribute:: baseline_fr


   .. py:attribute:: response_fr


   .. py:attribute:: latency


   .. py:attribute:: duration


   .. py:attribute:: dt


   .. py:attribute:: baseline_T


   .. py:attribute:: stimulus_T


   .. py:attribute:: total_bins


   .. py:attribute:: induce_refractory_period
      :value: False



   .. py:attribute:: kappa
      :value: 4



   .. py:attribute:: a
      :value: None



   .. py:attribute:: b
      :value: None



   .. py:attribute:: include_bursts
      :value: None



   .. py:attribute:: burst_rate_baseline
      :value: None



   .. py:attribute:: burst_rate_factor
      :value: None



   .. py:attribute:: burst_rate_response
      :value: None



   .. py:attribute:: burst_duration_lam
      :value: None



   .. py:attribute:: burst_response_time_factor
      :value: None



   .. py:attribute:: burst_alpha
      :value: None



   .. py:attribute:: burst_beta
      :value: None



   .. py:attribute:: burst_multiplier_baseline
      :value: None



   .. py:attribute:: burst_multiplier_response
      :value: None



   .. py:attribute:: r_t


   .. py:method:: induce_bursts(r_t, T_on, T_off, average_burst_rate, trial_section)


   .. py:method:: thin_indices(trial_activity, mean_fr, bin_centers, T_on, T_off, gt_mean, n_trials)

      Randomly thin spikes from a given section of the PSTH to match the ground truth
      firing rate.

      :param trial_activity: _description_
      :type trial_activity: _type_
      :param mean_fr: _description_
      :type mean_fr: _type_
      :param bin_centers: _description_
      :type bin_centers: _type_
      :param T_on: _description_
      :type T_on: _type_
      :param T_off: _description_
      :type T_off: _type_
      :param gt_mean: _description_
      :type gt_mean: _type_
      :param n_trials: _description_
      :type n_trials: _type_

      :returns: _description_
      :rtype: _type_



   .. py:method:: correct_bursts_to_target_firing_rates(trial_activity, n_trials, bin_size)

      Restore the simulated firing rates to the input/target firing rates,
      Calculates the discrepancy in the number of spikes between the ground-truth
      rate function and the measured mean firing rate.
      Thins spikes randomly within each baseline and response portion of the
      psth, across trials.
      To introduce some variation, the number of discrepant spikes are jittered
      by an amount sampled from a normal gaussian and scaled by the ground truth rate.

      :param trial_activity: _description_
      :type trial_activity: _type_
      :param n_trials: _description_
      :type n_trials: _type_
      :param bin_size: _description_
      :type bin_size: _type_

      :returns: _description_
      :rtype: _type_



   .. py:method:: generate_with_bursts(n_trials: int = 2, bin_size=25 / 1000)

      TODO: speed this up like 100000x

      :param n_trials: _description_. Defaults to 2.
      :type n_trials: int, optional
      :param bin_size: _description_. Defaults to 25/1000.
      :type bin_size: _type_, optional

      :returns: _description_
      :rtype: _type_



   .. py:method:: generate(n_trials: int = 1, squeeze: bool = True)

      Generate Poisson spike trains.

      :param n_trials: Number of trials to generate.
      :type n_trials: int, default=1
      :param squeeze: If True and n_trials==1, return a single 1D numpy array.
                      Otherwise, return a list of 1D numpy arrays.
      :type squeeze: bool, default=True

      :returns: **spikes** -- Spike times (seconds). 1D array if squeeze and n_trials==1, else list.
      :rtype: np.ndarray or list[np.ndarray]



