---
sidebar_position: 4
title: How it works
---
import stepFunctionImg from '@site/static/img/how-it-works/step_function.png';
import exampleUnit from '@site/static/img/how-it-works/example_unit.png';
import betaDist from '@site/static/img/how-it-works/beta_distribution.png';
import bursts from '@site/static/img/how-it-works/bursts.png';


<p style={{ fontSize: '0.85rem', color: 'gray', fontStyle: 'italic' }}>
  Updated May 2026 for the Uni. of Bonn MSc Computational Neuroscience module.
  <br />
  This page provides a general overview of the modeling approach used to generate the neuronal responses. For a more precise description of the methods used here, check out the cited resources.
</p>

# How it works

The response generator creates simulated single-neuron spike trains that look like stimulus-aligned neuronal recordings. 
The purpose is to generate populations of responsive and non-responsive units with controlled sets of parameters to test and compare methods for detecting stimulus-aligned responses.

We specifially want to generate convincing examples of human single unit responses, like the one below: 

<div style={{ textAlign: 'center' }}>
  <img
    src={exampleUnit}
    alt="Example responsive unit"
    style={{ width: '40%' }}
  />

  <p style={{ fontSize: '0.85rem', color: 'gray', fontStyle: 'italic' }}>
    Example responsive unit with the key response characteristics highlighted. 
  </p>
</div>

At a high level, the generator starts with a baseline firing rate, adds an optional stimulus-driven response, and then produces spike rasters across repeated trials. These simulated rasters can be used as ground-truth examples where the user knows whether a response was actually present.

## Approach

There are many ways to simulate neural responses. Since the goal here is to mimic the spiking activity of responsive single neurons, we model the overall behavior of the response as opposed to the generation process itself, with an emphasis on controlling the end response characteristics. 

To do this, we simulate the stimulus-aligned neuronal spiking using an [**inhomogenous Poisson process**](https://www.cns.nyu.edu/~david/handouts/poisson.pdf) [[1]](#ref-1). 

Generally, a poisson process is a stochastic model that describes the occurrence of random events over time or space [[2]](#ref-2), assuming that each event is indepedent of all other events. A homogenous Poisson process also assumes that each moment of time or parcel of space is equally likely to contain an event. A homogenous Poisson process could be used to generate spike counts in a set of bins with a fixed length, assuming that each bin has the same probability of producing a spike [[3]](#ref-3). With sufficiently short bins, we can use a Poisson process to model the probability of a single spike event, and thereby generate a spike train. A simple approach is: 

1. Set the instantaneous firing rate, $r$. 

2. Set the spike-train duration, $T$, and the bin width, $\Delta t$.

3. Compute the number of bins:

$$
N = T / \Delta t
$$

4. Draw one random number per bin:

$$
u_i \sim Uniform(0, 1), \quad i = 1, ..., N
$$

5. Compute the probability of a spike in each bin:

$$
p_s = r \Delta t
$$

6. Mark bin $i$ as containing a spike if:

$$
u_i \leq p_s
$$

7. Collect the spike times from the matching bin indices:

$$
t_i = i \Delta t
$$

❓ **Question:** The above algorithm generates a single spike train. How could you adapt it to produce a response raster? 



An inhomogenous Poisson process takes this approach one step further by assuming that the likelihood of a spike is not constant across time. Instead of a constant instantaneous firing rate, $r$, the inhomogenous form uses a time-varying firing rate, $r(t)$. 

We use an inhomogenous process to generate the responses, since it allows us to flexibly set the baseline and response firing rates. The simplest way to produce a response in this framework is to use a [step function](https://en.wikipedia.org/wiki/Step_function) as the rate function, where $r(t)$ is set to the baseline firing rate for all time points $t$ outside of the response period, and set to the response firing rate during the response period: 

<div style={{ textAlign: 'center' }}>
  <img
    src={stepFunctionImg}
    alt="Example rate function"
    style={{ width: '50%' }}
  />

  <p style={{ fontSize: '0.85rem', color: 'gray', fontStyle: 'italic' }}>
    Example inhomogeneous step-function firing rate.
  </p>
</div>

❓ **Question:** Does this look like a physiological response? Why or why not?

Since neuronal responses in the human medial temporal lobe don't generally behave like step functions, we use another way to model the response firing. Instead of uniformly increasing the instantaneous response fucntion during the response period, we replace the response period with a [Beta distribution](https://en.wikipedia.org/wiki/Beta_distribution) parameterized to decrease smoothly across the response period: 

<div style={{ textAlign: 'center' }}>
  <img
    src={betaDist}
    alt="Example rate function"
    style={{ width: '50%' }}
  />

  <p style={{ fontSize: '0.85rem', color: 'gray', fontStyle: 'italic' }}>
    Example inhomogeneous firing rate with a Beta-distributed response period. 
  </p>
</div>

❓ **Question:** Does this look like a physiological response? Why or why not?


## Adding variability 

Neural spike trains are not really Poisson processes, although this framework can be useful to describe spike trains. A major point absent from vanilla Poisson processes is the refractory period. 

❓ **Question:** Considering what we've discussed so far, what defining feature of a Poisson process contradicts the neuronal refractory period?

To remedy this, we induce refractory periods after generating the response raster. 

❓ **Question:** There are a few ways to do this. Can you think of a general method for enforcing a refractory period in already-generated data?

Last, neuronal spiking activity in the human cortex has a very distinctive property -- bursts. Bursts are brief periods of rapid firing activity and are usually associated with interneurons but show up in prinicipal cells as well. We include bursts by further modifying the rate function, $r(t)$:

<div style={{ textAlign: 'center' }}>
  <img
    src={bursts}
    alt="Bursting rate functions"
    style={{ width: '90%' }}
  />

  <p style={{ fontSize: '0.85rem', color: 'gray', fontStyle: 'italic' }}>
    Example responses without bursts (top row) and with bursts (bottom row).
  </p>
</div>

❓ **Question:** What additional simulation parameters do you think burst generation requires?

## Core parameters

Our model uses the following parameters:

| Parameter | Symbol | Description | Typical value / range |
|---|---:|---|---|
| Baseline firing rate | $r_\mathrm{base}$ | Average firing rate outside the stimulus-driven response period. | e.g. 0.1–50 Hz |
| Response firing rate | $r_\mathrm{response}$ | Peak firing rate during the stimulus-driven response. | e.g. greater than baseline |
| Response latency | $t_\mathrm{latency}$ | Time between stimulus onset and the start of the response. | e.g. 250–410 ms |
| Response duration | $t_\mathrm{duration}$ | Length of time over which the response is active. | e.g. 250–700 ms |
| Bin width | $\Delta t$ | Size of the time bins used when sampling spikes. | e.g. 1 ms |
| Number of trials | $n_\mathrm{trials}$ | Number of repeated stimulus presentations. | user-defined |
| Burst rate | $r_\mathrm{burst}$ | Rate at which short high-firing events are added. | optional |
| Burst duration | $t_\mathrm{burst}$ | Duration of each burst event. | optional |

These were chosen based on the characteristic features identified for single enurons recorded from the human medial temporal lobe. 

❓ **Question:** What are some other features that could have been included? Why might those be useful to simulate? 

## References

<a id="ref-1"></a>

[1] Heeger, D. (2000). *Poisson Model of Spike Generation*. New York University. https://www.cns.nyu.edu/~david/handouts/poisson.pdf

<a id="ref-2"></a>

[2] GeeksforGeeks. (2025). *Poisson Processes*. https://www.geeksforgeeks.org/maths/poisson-processes/

<a id="ref-3"></a>

[3] TU Chemnitz. *Model neurons: Poisson neurons*. https://www.tu-chemnitz.de/informatik/KI/scripts/ws0910/Neuron_Poisson.pdf