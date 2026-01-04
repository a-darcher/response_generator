%==========================================================================
% This script applies an analysis to identify concept cells in the
% simulated data using permutation testing.
%
% Tim Guth, 2025
%==========================================================================

% start
clc; close all; clear;

% fix random seed
rng(1);

% add functions and toolboxes
addpath(genpath('C:\Sciebo\GitCode\NeuroGuth\ConceptMuseum\Functions'));
addpath(genpath('C:\Sciebo\GitCode\NeuroGuth\ConceptMuseum\ConceptCells_20250310'));
addpath(genpath('C:\Sciebo\GitCode\NeuroGuth\ConceptMuseum\DoScreeningCombinato_20240822'));
addpath(genpath('D:\External\Functions'));

% pathsr
paths                           = struct();
%paths.data                      = 'E:\ConceptMuseum\ConceptCells_20250310\Simulations_20251022\100k';
%paths.save                      = 'E:\ConceptMuseum\ConceptCells_20250310\Simulations_20251022\100k';
paths.data                      = '/media/al/darch/response_stats/datasets/main/';
paths.save                      = paths.data;

% parameters
params                          = struct();
params.dataName                 = 'dataset.mat';
params.numSubsample             = 15000;
params.binwiseTestVersion       = 'original'; % 'original' or 'modified'
params.createFigure             = false;
params.timeRes                  = 0.05; % bin size for statistical test in seconds
params.smoothMethod             = 'movmean';
params.numSmoothBins            = 5; % number of bins for smoothing
params.minTime                  = -2; % start time of segment of interest in seconds
params.maxTime                  = 2; % end time of segment of interest in seconds
params.timeBaselineOn           = -1; % time of baseline onset in seconds
params.timeBaselineOff          = 0; % time of baseline offset in seconds
params.timeStimOn               = 0; % time of stimulus onset in seconds
params.timeStimOff              = 1; % time of stimulus offset in seconds
params.timeStimWindowOfInterest = [0.1, 0.9]; % time window of interest during stimulus presentation in seconds
params.timeBinsMinMax           = params.minTime:params.timeRes:params.maxTime;
params.timeCentersMinMax        = movmean(params.timeBinsMinMax, 2, 2, 'endpoints', 'discard');
params.timeCentersOfInterest    = params.timeCentersMinMax >= params.timeBaselineOn & params.timeCentersMinMax <= params.timeStimOff;
params.timeCenters              = params.timeCentersMinMax(params.timeCentersOfInterest);
params.numBins                  = sum(params.timeCentersOfInterest);
params.isBaselineBin            = params.timeCenters >= params.timeBaselineOn & params.timeCenters <= params.timeBaselineOff;
params.isStimBin                = params.timeCenters >= params.timeStimWindowOfInterest(1, 1) & params.timeCenters <= params.timeStimWindowOfInterest(1, 2);
params.minFractionActiveTrials  = 0.5;
params.alphaLevel               = 0.001;
params.nSur                     = 1001;
params.randSeeds                = randi(100001, [100001, 1]);
params.saveFolder               = ['examples_', num2str(params.numSubsample * 2), '_subsamples_', ...
    num2str(params.nSur), '_surrogates_', extractAfter(num2str(params.alphaLevel), '.'), ...
    '_alpha_', params.binwiseTestVersion, '_binwise_tests'];

% create folder for results
if ~isfolder(fullfile(paths.save, params.saveFolder))
    mkdir(fullfile(paths.save, params.saveFolder));
end

% save settings
save(fullfile(paths.save, params.saveFolder, 'settings'));

%% load data

% all data
data                            = load(fullfile(paths.save, params.dataName));
data                            = data.data;

% ground truth
duration                        = data.duration;
frBaseline                      = data.fr_baseline;
frStimulus                      = data.fr_response;
isResponse                      = logical(data.response);
numTrials                       = cellfun(@(x) size(x, 2), data.rasters);
isConsidered                    = numTrials >= 5;
allStimSpikeTimes               = data.rasters;
allBaseSpikeTimes               = data.supp_rasters;

% subsample to n examples per condition
respIdx                         = find(isResponse & isConsidered);
nonRespIdx                      = find(~isResponse & isConsidered);
respSel                         = randsample(respIdx, params.numSubsample);
nonRespSel                      = randsample(nonRespIdx, params.numSubsample);
selIdx                          = sort([respSel, nonRespSel]);

% select data
duration                        = duration(selIdx);
frBaseline                      = frBaseline(selIdx);
frStimulus                      = frStimulus(selIdx);
isResponse                      = isResponse(selIdx);
numTrials                       = numTrials(selIdx);
allStimSpikeTimes               = allStimSpikeTimes(selIdx);
allBaseSpikeTimes               = allBaseSpikeTimes(selIdx);

% loop through units
pPerm                           = NaN(size(allStimSpikeTimes));
pRanksum                        = NaN(size(allStimSpikeTimes));
pSignrank                       = NaN(size(allStimSpikeTimes));
parfor iUnit = 1:size(allStimSpikeTimes, 2)
    try

        % display progress
        disp(iUnit);

        % fix random seed
        rng(params.randSeeds(iUnit));

        %% get data of this unit

        % stimulus and baseline
        stimulusSpikeTimes              = allStimSpikeTimes{1, iUnit}';
        baselineSpikeTimes              = allBaseSpikeTimes{1, iUnit}';

        % concatenate data
        spikeTimes                      = cat(1, stimulusSpikeTimes, baselineSpikeTimes);
     %   spikeTimes                      = stimulusSpikeTimes;

        % cue index
        isCue                           = cat(1, true(size(stimulusSpikeTimes)), false(size(baselineSpikeTimes)));

        %% firing rate map

        % compute firing rate map
        counts              = zeros(size(spikeTimes, 1), numel(params.timeBinsMinMax) - 1);
        for iTrial = 1:size(spikeTimes, 1)
            counts(iTrial, :)   = histcounts(spikeTimes{iTrial, :}, params.timeBinsMinMax);
        end
        FR                  = counts / params.timeRes;

        % smooth firing rate
        smFR                = smoothdata(FR, 2, params.smoothMethod, params.numSmoothBins);

        % cut firing rate window to time window of interest
        FR                  = FR(:, params.timeCentersOfInterest);
        smFR                = smFR(:, params.timeCentersOfInterest);

        % cue firing rates
        cueFR               = FR(isCue, :);
        cueSmFR             = smFR(isCue, :);

        %% cluster-based permutation test

        % compute maximum t-valueisCue
        t                   = TG_ComputeStatistic_20251013(smFR, isCue, params);

        % compute surrogate test statistics
        tSur                = NaN(1, params.nSur);

        for iSur = 1:params.nSur

            % values for random shifts of each cue period
            randShifts          = randi(params.numBins, [sum(isCue), 1]);

            % compute new bin indices
            binIdx              = mod((0:params.numBins - 1) - randShifts, params.numBins) + 1;

            % stimulus indices for all bins
            stimIdx             = repmat((1:sum(isCue))', 1, params.numBins);

            % use linear indexing to extract shifted values
            surCueSmFR          = cueSmFR(sub2ind([sum(isCue), params.numBins], stimIdx, binIdx));

            % surrogate firing rates
            surSmFR             = smFR;
            surSmFR(isCue, :)   = surCueSmFR;

            % compute surrogate test statistic
            [tSur(1, iSur), ~]  = TG_ComputeStatistic_20251013(surSmFR, isCue, params);
        end

        % compute rank of empirical t-value in surrogat t-values
        permRank            = sum(t > tSur) / params.nSur;

        % correct rank
        if (sum(any(cueFR(:, params.isStimBin) > 0, 2)) / sum(isCue)) < params.minFractionActiveTrials
            permRank            = 0;
        end

        % p-value
        pPerm(1, iUnit)     = 1 - permRank;

        %% binwise ranksum test

        % calculate binwise ranksum
        considerRanksum     = [];
        if strcmp(params.binwiseTestVersion, 'modified')
            [pRanksum(1, iUnit), considerRanksum, ~]    = TG_binwise_ranksum_20251023(...
                cellfun(@(x) x * 1000, spikeTimes(isCue, :), 'Uni', 0), ...
                cellfun(@(x) x * 1000, spikeTimes, 'Uni', 0), ...
                [params.timeBaselineOn * 1000, params.timeBaselineOff * 1000], ...
                [params.timeStimOn * 1000, params.timeStimOff * 1000], ...
                100, params.alphaLevel, params.minFractionActiveTrials, true, [], 0.6, false);
        elseif strcmp(params.binwiseTestVersion, 'original')
            [pRanksum(1, iUnit), considerRanksum, ~]    = binwise_ranksum(...
                cellfun(@(x) x * 1000, spikeTimes(isCue, :), 'Uni', 0), ...
                cellfun(@(x) x * 1000, spikeTimes, 'Uni', 0), ...
                [params.timeBaselineOn * 1000, params.timeBaselineOff * 1000], ...
                [params.timeStimOn * 1000, params.timeStimOff * 1000], ...
                100, params.alphaLevel, params.minFractionActiveTrials, true, [], 0.6, false);
        end

        % consider ranksum test?
        if ~considerRanksum
            pRanksum(1, iUnit)  = 1;
        end
        %% binwise signed rank test

        considerSignrank    = [];
        if strcmp(params.binwiseTestVersion, 'modified')
            [pSignrank(1, iUnit), considerSignrank]     = TG_binwise_signed_rank_20251023(...
                cellfun(@(x) x * 1000, spikeTimes(isCue, :), 'Uni', 0), ...
                [params.timeBaselineOn * 1000, params.timeBaselineOff * 1000], ...
                [params.timeStimOn * 1000, params.timeStimOff * 1000], ...
                100, params.alphaLevel, params.minFractionActiveTrials, true);
        elseif strcmp(params.binwiseTestVersion, 'original')
            [pSignrank(1, iUnit), considerSignrank]     = binwise_signed_rank(...
                cellfun(@(x) x * 1000, spikeTimes(isCue, :), 'Uni', 0), ...
                [params.timeBaselineOn * 1000, params.timeBaselineOff * 1000], ...
                [params.timeStimOn * 1000, params.timeStimOff * 1000], ...
                100, params.alphaLevel, params.minFractionActiveTrials, true);
        end

        % consider signed rank test?
        if ~considerSignrank
            pSignrank(1, iUnit) = 1;
        end
        %% create plot

        % if there is a deviation from ground truth
        if ((pPerm(1, iUnit) < params.alphaLevel) ~= isResponse(1, iUnit) || ...
                (pRanksum(1, iUnit) < params.alphaLevel) ~= isResponse(1, iUnit) || ...
                (pSignrank(1, iUnit) < params.alphaLevel) ~= isResponse(1, iUnit)) ...
                && params.createFigure

            % create figure
            responseFigure      = figure('Units', 'normalized', 'Position', [0.1, 0.1, 0.2, 0.85], 'Visible', 'off');
            ax                  = axes('Units', 'normalized', 'Position', [0, 0, 1, 1], 'Visible', 'off');

            %% raster plot

            % get cue spikes
            cueSpikeTimes       = spikeTimes(isCue, :);

            % create axis
            axSpikes            = axes('Position', [0.16, 0.65, 0.8, 0.3]);

            % loop through cues
            for iCue = 1:sum(isCue)

                % plot horizontal lines for each spike
                yVal                    = iCue * ones(size(cueSpikeTimes{iCue, 1}));
                for iSpike = 1:size(cueSpikeTimes{iCue, 1}, 2)
                    line([cueSpikeTimes{iCue, 1}(iSpike), cueSpikeTimes{iCue, 1}(iSpike)], [yVal(iSpike) - 0.4, yVal(iSpike) + 0.4], 'Color', [0, 0, 0, 0.7], 'LineWidth', 1);
                end
            end

            % stimulus onset
            xline(params.timeStimOn, 'LineWidth', 1, 'LineStyle', '-', 'Color', [1, 0.2, 0, 0.7]);

            % settings
            xlim([params.minTime, params.maxTime]);
            xticks([params.minTime, 0, params.maxTime]);
            ylim([0, sum(isCue) + 1]);
            ylabel('Stimulus');
            set(gca, 'YDir', 'reverse', 'Box', 'off', 'TickDir', 'out', 'XColor', 'none');

            %% firing rate plot

            % create axis
            axFR                = axes('Position', [0.16, 0.49, 0.8, 0.14]);

            % plot firing rate
            TG_ShadeSEM_20250317(params.timeCenters, FR(isCue, :), [0, 0, 0], 0.5);
            xline(params.timeStimOn, 'LineWidth', 1, 'LineStyle', '-', 'Color', [1, 0.2, 0, 0.7]);
            xlabel('Time (s)');
            ylabel('Firing rate (Hz)');
            set(gca, 'Box', 'off', 'TickDir', 'out');

            % link axes
            linkaxes([axSpikes, axFR], 'x');

            %% permutation test plot

            % surrogate and empirical t-value plot
            axHist          = axes('Position', [0.16, 0.28, 0.8, 0.15]);
            histogram(tSur, 'FaceColor', [0.5, 0.5, 0.5], 'FaceAlpha', 1);
            set(gca, 'tickDir', 'out', 'box', 'off');
            xline(t, 'Color', 'r', 'LineWidth', 2);
            xlabel('Surrogate t-values');
            ylabel('Number of surrogates');

            %% plot additional information

            % plot whether responsive unit or not
            if isResponse(1, iUnit) == 1
                title(axSpikes, 'Responsive cell (ground truth)');
            else
                title(axSpikes, 'Non-responsive cell (ground truth)');
            end

            % plot permutation test p-values
            if (pPerm(1, iUnit) < params.alphaLevel) ~= isResponse(1, iUnit)
                text(ax, 0.2, 0.2, sprintf('P_{permutation} = %.3f', pPerm(1, iUnit)), 'Color', 'r');
            else
                text(ax, 0.2, 0.2, sprintf('P_{permutation} = %.3f', pPerm(1, iUnit)), 'Color', 'g');
            end

            % plot ranksum test p-values
            if (pRanksum(1, iUnit) < params.alphaLevel) ~= isResponse(1, iUnit)
                text(ax, 0.2, 0.17, sprintf('P_{ranksum} = %.3f', pRanksum(1, iUnit)), 'Color', 'r');
            else
                text(ax, 0.2, 0.17, sprintf('P_{ranksum} = %.3f', pRanksum(1, iUnit)), 'Color', 'g');
            end

            % plot signrank test p-values
            if (pSignrank(1, iUnit) < params.alphaLevel) ~= isResponse(1, iUnit)
                text(ax, 0.2, 0.14, sprintf('P_{signrank} = %.3f', pSignrank(1, iUnit)), 'Color', 'r');
            else
                text(ax, 0.2, 0.14, sprintf('P_{signrank} = %.3f', pSignrank(1, iUnit)), 'Color', 'g');
            end

            % plot further ground truth information
            text(ax, 0.2, 0.11, sprintf('Response duration = %.3f s', duration(1, iUnit)));
            text(ax, 0.2, 0.08, sprintf('Firing rate_{baseline} = %.3f Hz', frBaseline(1, iUnit)));
            text(ax, 0.2, 0.05, sprintf('Firing rate_{stimulus} = %.3f Hz', frStimulus(1, iUnit)));

            % adjust font size
            set(findall(responseFigure, '-property', 'FontSize'), 'FontSize', 12);

            %% save figure

            % incorrect test conditions
            labels      = {'RanksumTestFalsePositives', 'RanksumTestFalseNegatives', ...
                'SignrankTestFalsePositives', 'SignrankTestFalseNegatives', ...
                'PermutationTestFalsePositives', 'PermutationTestFalseNegatives'};
            conditions  = [ ...
                ~isResponse(1, iUnit) && pRanksum(1, iUnit) < params.alphaLevel, ...
                isResponse(1, iUnit) && pRanksum(1, iUnit) >= params.alphaLevel, ...
                ~isResponse(1, iUnit) && pSignrank(1, iUnit) < params.alphaLevel, ...
                isResponse(1, iUnit) && pSignrank(1, iUnit) >= params.alphaLevel, ...
                ~isResponse(1, iUnit) && pPerm(1, iUnit) < params.alphaLevel, ...
                isResponse(1, iUnit) && pPerm(1, iUnit) >= params.alphaLevel];

            % save figure
            for idx = find(conditions)

                % save path
                savePath = fullfile(paths.save, params.saveFolder, labels{idx});
                if sum(isCue) <= 5
                    savePath = fullfile(savePath, 'FiveTrials');
                end
                if ~isfolder(savePath)
                    mkdir(savePath);
                end
                exportgraphics(responseFigure, fullfile(savePath, ['Unit_', num2str(selIdx(iUnit)), '.jpg']));
            end

            % close figure
            close(responseFigure);
        end
    catch ME
        warning(['Error in iteration ', num2str(iUnit), ': ', ME.message]);
        continue;
    end
end

%% save results
save(fullfile(paths.save, params.saveFolder, 'allRes'), ...
    'params', 'paths', 'selIdx', 'numTrials', 'duration', ...
    'frBaseline', 'frStimulus', 'isResponse', 'pPerm', 'pRanksum', 'pSignrank');

%% plot as a function of trial number

% load results
r           = load(fullfile(paths.save, params.saveFolder, 'allRes'));

% percentile split of trial numbers
percentiles = prctile(r.numTrials, 0:5:100);

% create percentile labels
percentileLabels = strings(1, size(percentiles, 2) - 1);
for iPercentile = 1:(size(percentiles, 2) - 1)
    percentileLabels(iPercentile) = sprintf('%d-%d', percentiles(iPercentile), percentiles(iPercentile + 1));
end

% test labels
testNames       = {'Ranksum FP', 'Ranksum FN', 'Signrank FP', 'Signrank FN', 'Permutation FP', 'Permutation FN'};

% preallocate results table
percentileRes   = table('Size', [size(testNames, 2), size(percentileLabels, 2)], 'VariableTypes', repmat({'double'}, 1, size(percentileLabels, 2)), ...
    'VariableNames', cellstr(percentileLabels));

% loop through percentiles
for iPercentile = 1:size(percentileLabels, 2)

    % get trial index of this percentile
    isThisDecile    = r.numTrials >= percentiles(iPercentile) & r.numTrials < percentiles(iPercentile + 1);

    % ranksum test
    ranksumFP           = sum(~r.isResponse(isThisDecile) & (r.pRanksum(isThisDecile) < r.params.alphaLevel)) ...
        / sum(~r.isResponse(isThisDecile)) * 100;
    ranksumFN           = sum(r.isResponse(isThisDecile) & (r.pRanksum(isThisDecile) >= r.params.alphaLevel)) ...
        / sum(r.isResponse(isThisDecile)) * 100;

    % signrank test
    signrankFP          = sum(~r.isResponse(isThisDecile) & (r.pSignrank(isThisDecile) < r.params.alphaLevel)) ...
        / sum(~r.isResponse(isThisDecile)) * 100;
    signrankFN          = sum(r.isResponse(isThisDecile) & (r.pSignrank(isThisDecile) >= r.params.alphaLevel)) ...
        / sum(r.isResponse(isThisDecile)) * 100;

    % permutation test
    permFP              = sum(~r.isResponse(isThisDecile) & (r.pPerm(isThisDecile) < r.params.alphaLevel)) ...
        / sum(~r.isResponse(isThisDecile)) * 100;
    permFN              = sum(r.isResponse(isThisDecile) & (r.pPerm(isThisDecile) >= r.params.alphaLevel)) ...
        / sum(r.isResponse(isThisDecile)) * 100;

    % assign to table
    percentileRes{1, iPercentile} = ranksumFP;
    percentileRes{2, iPercentile} = ranksumFN;
    percentileRes{3, iPercentile} = signrankFP;
    percentileRes{4, iPercentile} = signrankFN;
    percentileRes{5, iPercentile} = permFP;
    percentileRes{6, iPercentile} = permFN;
end

% add row names
percentileRes.Properties.RowNames = testNames;

% display results
fprintf('\nPercentile-based false positives and false negatives (%%):\n\n');
disp(percentileRes);

%% plot false positives and false negatives

% create figure
falsePosAndNegFig = figure;

% x-values
xVals  = 1:size(percentileRes, 2);

%% false positives

% plot lines
subplot(2, 2, 1);
p1  = plot(xVals, percentileRes{'Ranksum FP', :},  '-o', 'LineWidth', 1.5, 'MarkerSize', 5); hold on;
p2  = plot(xVals, percentileRes{'Signrank FP', :}, '-s', 'LineWidth', 1.5, 'MarkerSize', 5);
p3  = plot(xVals, percentileRes{'Permutation FP', :}, '-^', 'LineWidth', 1.5, 'MarkerSize', 5);

% axes
xlabel('Trial numbers (percentiles)');
ylabel('False positives (%)');
title('False positives as a function of trial number');
xlim([xVals(1) - 0.5, xVals(end) + 0.5]);
ylim([0, 100]);
set(gca, 'TickDir', 'out', 'Box', 'off', 'XTick', xVals, 'XTickLabel', percentileLabels);

% legend
legend([p1, p2, p3], {...
    sprintf('Ranksum (α = %.3f); Mean across trials: %.3f %%', ...
    r.params.alphaLevel, sum(r.isResponse == 0 & (r.pRanksum < r.params.alphaLevel)) / ...
    sum(r.isResponse == 0) * 100), ...
    sprintf('Signed rank (α = %.3f); Mean across trials: %.3f %%', ...
    r.params.alphaLevel, sum(r.isResponse == 0 & (r.pSignrank < r.params.alphaLevel)) / ...
    sum(r.isResponse == 0) * 100), ...
    sprintf('Permutation (α = %.3f); Mean across trials: %.3f %%', ...
    r.params.alphaLevel, sum(r.isResponse == 0 & (r.pPerm < r.params.alphaLevel)) / ...
    sum(r.isResponse == 0) * 100), ...
    }, 'Location', 'northeast');

% plot lines
subplot(2, 2, 2);
plot(xVals, percentileRes{'Ranksum FP', :},  '-o', 'LineWidth', 1.5, 'MarkerSize', 5); hold on;
plot(xVals, percentileRes{'Signrank FP', :}, '-s', 'LineWidth', 1.5, 'MarkerSize', 5);
plot(xVals, percentileRes{'Permutation FP', :}, '-^', 'LineWidth', 1.5, 'MarkerSize', 5);

% axes
xlabel('Trial numbers (percentiles)');
ylabel('False positives (%)');
title('False positives as a function of trial number');
xlim([xVals(1) - 0.5, xVals(end) + 0.5]);
ylim([0, min([10, ceil(max([percentileRes{'Ranksum FP', :}, percentileRes{'Signrank FP', :}, percentileRes{'Permutation FP', :}]))])]);
set(gca, 'TickDir', 'out', 'Box', 'off', 'XTick', xVals, 'XTickLabel', percentileLabels);

%% false negatives

% plot lines
subplot(2, 2, 3);
q1  = plot(xVals, percentileRes{'Ranksum FN', :},  '-o', 'LineWidth', 1.5, 'MarkerSize', 5); hold on;
q2  = plot(xVals, percentileRes{'Signrank FN', :}, '-s', 'LineWidth', 1.5, 'MarkerSize', 5);
q3  = plot(xVals, percentileRes{'Permutation FN', :}, '-^', 'LineWidth', 1.5, 'MarkerSize', 5);

% axes
xlabel('Trial numbers (percentiles)');
ylabel('False negatives (%)');
title('False negatives as a function of trial number');
xlim([xVals(1) - 0.5, xVals(end) + 0.5]);
ylim([0, 100]);
set(gca, 'TickDir', 'out', 'Box', 'off', 'XTick', xVals, 'XTickLabel', percentileLabels);

% legend
legend([q1, q2, q3], {...
    sprintf('Ranksum (α = %.3f); Mean across trials: %.3f %%', ...
    r.params.alphaLevel, sum(r.isResponse == 1 & (r.pRanksum >= r.params.alphaLevel)) / ...
    sum(r.isResponse == 0) * 100), ...
    sprintf('Signed rank (α = %.3f); Mean across trials: %.3f %%', ...
    r.params.alphaLevel, sum(r.isResponse == 1 & (r.pSignrank >= r.params.alphaLevel)) / ...
    sum(r.isResponse == 0) * 100), ... 
    sprintf('Permutation (α = %.3f); Mean across trials: %.3f %%', ...
    r.params.alphaLevel, sum(r.isResponse == 1 & (r.pPerm >= r.params.alphaLevel)) / ...
    sum(r.isResponse == 0) * 100), ...
    }, 'Location', 'northeast');

% plot lines
subplot(2, 2, 4);
plot(xVals, percentileRes{'Ranksum FN', :},  '-o', 'LineWidth', 1.5, 'MarkerSize', 5); hold on;
plot(xVals, percentileRes{'Signrank FN', :}, '-s', 'LineWidth', 1.5, 'MarkerSize', 5);
plot(xVals, percentileRes{'Permutation FN', :}, '-^', 'LineWidth', 1.5, 'MarkerSize', 5);

% axes
xlabel('Trial numbers (percentiles)');
ylabel('False negatives (%)');
title('False negatives as a function of trial number');
xlim([xVals(1) - 0.5, xVals(end) + 0.5]);
ylim([0, min([10, ceil(max([percentileRes{'Ranksum FN', :}, percentileRes{'Signrank FN', :}, percentileRes{'Permutation FN', :}]))])]);
set(gca, 'TickDir', 'out', 'Box', 'off', 'XTick', xVals, 'XTickLabel', percentileLabels);

% save figure
exportgraphics(falsePosAndNegFig, fullfile(r.paths.save, r.params.saveFolder, 'FalsePositivesAndNegatives.jpg'));

%% save results
save(fullfile(paths.save, params.saveFolder, 'allRes'), ...
    'params', 'paths', 'selIdx', 'numTrials', 'duration', 'percentileRes', ...
    'frBaseline', 'frStimulus', 'isResponse', 'pPerm', 'pRanksum', 'pSignrank');
