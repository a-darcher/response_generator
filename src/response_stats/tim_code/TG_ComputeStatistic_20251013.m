function [t, isMax] = TG_ComputeStatistic_20251013(FR, isCue, params)
%
% TG_ComputeStatistic computes the maximum t-value
% across stimulus bins and returns its global bin index.
%
% Input:
%   FR          - firing rates (trials x bins)
%   isCue       - logical index for stimulus-of-interest trials
%   params      - time bin parameters
%
% Output:
%
%   t           - maximum t-value
%   isMax       - index of maximum t-value
%
% Tim Guth, 2025

% stimulus and baseline firing rates
stimulusFR              = FR(isCue, params.isStimBin);
baselineFR              = FR(:, params.isBaselineBin);
meanBaselineFR          = mean(baselineFR, 2);

% candidate cluster
[~, ~, ~, stats]        = ttest2(stimulusFR, repmat(meanBaselineFR, [1, size(stimulusFR, 2)]), 'Tail', 'right', 'Vartype', 'unequal');
testStat                = stats.tstat;

% find maximum t-value and its location
[t, maxIdx]             = max(testStat);
isMax                   = false(1, size(FR, 2));
isStimMax               = isMax(params.isStimBin);
isStimMax(maxIdx)       = true;
isMax(params.isStimBin) = isStimMax;
end