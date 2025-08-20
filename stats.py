import numpy as np
from scipy.stats import mannwhitneyu, wilcoxon

baseline_bins = [0, baseline_T] # count spikes during entire baseline period, already in Hz
baseline_hist = np.array([np.histogram(trial, baseline_bins)[0] for trial in trial_activity]).ravel()
assert sum(baseline_hist) == sum([sum(t <= 1) for t in trial_activity]), "Binned baseline spikes do not match number of baseline spikes."

# interleave
bin_width = 0.1

bins_straight_up = np.arange(baseline_T, (baseline_T + stimulus_T)+bin_width, bin_width)
bins_betweeners = np.arange(baseline_T+(bin_width/2), (baseline_T + stimulus_T), bin_width)

# bin data, spike count / 100 ms
hist_straight_up = np.array([np.histogram(trial, bins_straight_up)[0] for trial in trial_activity])
hist_betweeners = np.array([np.histogram(trial, bins_betweeners)[0] for trial in trial_activity])

assert hist_straight_up.sum() == sum([sum(t > 1) for t in trial_activity]), "Binned stimulus spikes (full period) do not match number of total stimulus spikes."
lower = baseline_T + bin_width/2
upper = baseline_T + stimulus_T - bin_width/2
assert (hist_betweeners).sum() == sum([sum((t > lower) & (t < upper)) for t in trial_activity]), "Binned stimulus spikes (interleaved period) do not match number of total stimulus spikes."

interleaved = np.zeros((len(trial_activity), len(bins_straight_up)+len(bins_betweeners)-2), int)
interleaved[:, ::2] = hist_straight_up
interleaved[:, 1::2] = hist_betweeners
assert interleaved.sum() == hist_betweeners.sum() + hist_straight_up.sum(), "Interleaved matrix does not included the expected number of spikes."

# convert to rate per second, from rate per (bin width)
interleaved = interleaved * stimulus_T / bin_width



proportion_active = (1/3)
direction="positive"



n_bins = interleaved.shape[1]
n_trials = interleaved.shape[0]


atrials = interleaved.any(1).sum()

pvals_binwise = np.ones(n_bins)
direction_of_bin = np.zeros(n_bins, dtype=bool)

# count number of spikes in baseline for determining response direction
baseline_sum = baseline_hist.sum()

if atrials > n_trials * proportion_active:
    
    
    for bin_i in range(n_bins):
        if (baseline_hist - interleaved[:, bin_i]).any():
            _, pval = wilcoxon(interleaved[:, bin_i], baseline_hist)
        
        elif not (baseline_hist - interleaved[:, bin_i]).any():
            pval = -1
        
        direction_of_bin[bin_i] = interleaved[:, bin_i].sum() >= baseline_sum

        pvals_binwise[bin_i] = pval

    # restrict response search based on the direction of the response
    # by forcing bins with conflicting direction to have a value of 1.
    pvals_binwise[~direction_of_bin] = 1
    
    # apply Simes 
    pvals_binwise.sort()
    pvals_binwise *=  n_bins / np.arange(1, n_bins + 1)

pval_abs = np.abs(pvals_binwise)

pval_surviving = pval_abs.min()
print("surviving pval", pval_surviving)
