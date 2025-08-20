import numpy as np

class PoissonSpikeGenerator:
    def __init__(self, baseline_fr, response_fr, 
                 latency, duration, dt, baseline_T, stimulus_T, 
                 induce_refractory_period=False, kappa=4):
        self.baseline_fr = baseline_fr
        self.response_fr = response_fr
        self.latency = latency
        self.duration = duration
        self.dt = dt
        self.baseline_T = baseline_T
        self.stimulus_T = stimulus_T

        self.total_bins = int((baseline_T + stimulus_T) / dt)

        self.induce_refractory_period = induce_refractory_period
        self.kappa = kappa

        self.r_t = self._build_rate_function()
        
    def _build_rate_function(self):
        r_t = np.ones(self.total_bins, dtype=int)

        #r_t[:int(self.baseline_T/self.dt)] = self.baseline_fr

        r_t[:] = self.baseline_fr

        response_onset = int(self.latency / self.dt) + int(self.baseline_T / self.dt)
        response_offset = int((self.latency / self.dt) + int(self.duration / self.dt)) + int(self.baseline_T / self.dt) 

        r_t[response_onset:response_offset] = self.response_fr

        return r_t
    
    def _force_renewal_process(self, spike_train, kappa):
        """
        Induce a refractory period by removing every k-th spike.
        This will results in a spike train with ISIs following a gamma pdf.
        """
        mask = np.arange(kappa-1, spike_train.size, kappa)
        return spike_train[mask]
    
    def generate_trial(self):

        spike_train = []
        
        t = 0
        while t < (self.baseline_T + self.stimulus_T) / self.dt:
            x_i = np.random.random()
            r_i = self.r_t[t]

            if x_i <= r_i * self.dt:
                spike_train.append(t * self.dt)
            t += 1

        if self.induce_refractory_period:
            spike_train = self._force_renewal_process(np.array(spike_train), self.kappa)

        return np.array(spike_train)
    
    def generate_trials(self, n_trials):
        return [self.generate_trial() for _ in range(n_trials)]

