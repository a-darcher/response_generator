pipeline
========

.. py:module:: pipeline


Functions
---------

.. autoapisummary::

   pipeline.fig_to_base64_png
   pipeline.make_preview_figure
   pipeline.generate_preview


Module Contents
---------------

.. py:function:: fig_to_base64_png(fig) -> str

.. py:function:: make_preview_figure(n_trials: int, baseline_fr: float, response_fr: float, duration: float, latency: float, a: float | None, b: float | None, baseline_T: float, stimulus_T: float, dt: float, induce_refractory_period: bool, generator: response_generator.generators.PoissonSpikeGenerator, trial_activity: List[numpy.ndarray]) -> matplotlib.pyplot.Figure

.. py:function:: generate_preview(baseline_fr: float, response_fr: float, latency: float, duration: float, baseline_T: float, stimulus_T: float, dt: float, induce_refractory_period: bool, rng: Any, a: float | None, b: float | None, include_bursts: bool, burst_rate_baseline: float, burst_rate_response: float, burst_response_time_factor: float, burst_duration_lam: float, burst_alpha: float, burst_beta: float, burst_multiplier: float, n_trials: int) -> dict[str, Any]

