%==========================================================================
% This script applies an analysis to identify concept cells in the
% Concept Museum using permutation testing.
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
addpath(genpath('D:\External\Toolboxes\MatNWB_v290'));

% paths
paths                           = struct();
paths.nwbData                   = 'E:\ConceptMuseum\DataInNWB_20240206';
paths.save                      = 'E:\ConceptMuseum\ConceptCells_20250310\ResultsPermutationTest_20251104';

% create folder for concept cells
if ~isfolder(fullfile(paths.save, 'ConceptCells'))
    mkdir(fullfile(paths.save, 'ConceptCells'));
end

% sessions
sessions                        = dir(fullfile(paths.nwbData, '*complete*.nwb'));

% parameters
params                          = struct();
params.createFigure             = true;
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
params.alphaLevel               = 0.05;
params.bonferroniCorrection     = true;
params.nSurHistBins             = 20;
params.nSur                     = 10001;
params.randSeeds                = randi(10001, [1001, 1]);

% save settings
save(fullfile(paths.save, 'settings'));

% preallocate
allRes                          = cell(size(sessions));

%% loop through sessions
for iSess = 1:size(sessions, 1)

    % clear variables
    close all; clearvars -except paths sessions params allRes iSess

    % display progress
    disp(sessions(iSess).name);

    %% load NWB file

    % read NWB file
    nwb                             = nwbRead(fullfile(paths.nwbData, sessions(iSess).name));

    % save folder
    savePath                        = fullfile(paths.save, extractBefore(sessions(iSess).name, '.nwb'));
    if ~isfolder(savePath)
        mkdir(savePath);
    end
    if ~isfolder(fullfile(savePath, 'ItemResponsiveCells'))
        mkdir(fullfile(savePath, 'ItemResponsiveCells'));
    end
    if ~isfolder(fullfile(savePath, 'ConceptCells'))
        mkdir(fullfile(savePath, 'ConceptCells'));
    end

    %% subject and session ID

    % extract from NWB idenifier
    identifierSplit                 = strsplit(nwb.identifier, '_');
    subjectAndSessionStr            = identifierSplit(cellfun(@(x) all(isstrprop(x, 'digit')), identifierSplit));
    subjectAndSession               = str2double(subjectAndSessionStr);

    %% single-unit data

    % read in single-unit data
    unitTable                       = nwb.units.toTable;
    microSr                         = nwb.acquisition.get('data_microelectrodes').starting_time_rate;

    %% electrodes

    % electrode data
    elecTable                       = nwb.general_extracellular_ephys_electrodes.toTable();

    %% get cue information from NWB file

    % load cue images
    cueImages                       = nwb.stimulus_templates.get('images').baseimage.values;

    % cue table
    cueTable                        = nwb.intervals.get('cue').toTable;

    % screening cue table
    screeningCueTable               = [];
    try
        screeningCueTable                               = nwb.intervals.get('screening_cue').toTable;
    catch
        screeningCueTable.start_time                    = [];
        screeningCueTable.stop_time                     = [];
        screeningCueTable.index_of_cue_image            = [];
        screeningCueTable.name_of_cue_image             = [];
        screeningCueTable.showing_image_instead_of_word = logical([]);
        warning('No screening.');
    end

    % extract cue times
    cueStarts                       = cat(1, cueTable.start_time, screeningCueTable.start_time);

    % screening cue index
    cueScreeningIdx                 = cat(1, zeros(size(cueTable.start_time)), ones(size(screeningCueTable.start_time)));

    % cue image index
    cueImgIdx                       = cat(1, cueTable.index_of_cue_image, screeningCueTable.index_of_cue_image);

    % cue image name
    cueImgName                      = cat(1, cueTable.name_of_cue_image, screeningCueTable.name_of_cue_image);

    % showing image instead of word
    cueImgNotWord                   = cat(1, cueTable.showing_image_instead_of_word, screeningCueTable.showing_image_instead_of_word);

    % full cue name
    cueImgNameFull                  = cueImgName;
    cueImgNameFull(cueImgNotWord)   = strcat(cueImgNameFull(cueImgNotWord), '_image');
    cueImgNameFull(~cueImgNotWord)  = strcat(cueImgNameFull(~cueImgNotWord), '_word');

    % lookup table
    uniqueCues                      = sort(unique(cueImgNameFull));

    %% unit-wise results

    % preallocate
    sessRes                         = struct(...
        'subjectID', [], 'sessionID', [], 'unitID', [], 'brainRegion', [], ...
        'cues', [], 'maxTval', [], 'rankPermutationTest', [], ...
        'pValueRanksum', [], 'considerRanksum', [], ...
        'isConceptCell', []);

    % loop through units
    parfor (iUnit = 1:size(unitTable, 1), 8)

        % display progress
        disp(iUnit);

        % fix random seed
        rng(params.randSeeds(iUnit));

        %% electrode index

        % get from electrode table
        electrodeIdx        = unitTable.electrodes(iUnit, 1);
        thisElecInfo        = elecTable(elecTable.id == electrodeIdx, :);
        thisLabel           = thisElecInfo.label{:};

        %% get unit spikes

        % get data of this unit
        thisUnit            = unitTable(iUnit, :);

        % get spike times
        thisUnitSpikeTimes  = thisUnit.spike_times{:};

        %% get unit brain region
        brainRegion         = thisElecInfo.location{:};

        %% all spike times
        spikeTimes          = cell(size(cueStarts));
        stimSpikeTimes      = cell(size(cueStarts));
        blSpikeTimes        = cell(size(cueStarts));
        for iCue = 1:size(cueStarts, 1)

            % get all spike times
            bCue                    = thisUnitSpikeTimes >= (cueStarts(iCue) + params.minTime) & thisUnitSpikeTimes <= (cueStarts(iCue) + params.maxTime);
            spikeTimes{iCue}        = thisUnitSpikeTimes(bCue) - cueStarts(iCue);
        end

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

        %% analyze stimuli

        % loop through stimuli
        isCue               = cell(size(uniqueCues));
        cueFR               = cell(size(uniqueCues));
        t                   = NaN(size(uniqueCues));
        isMax               = false(size(uniqueCues, 1), params.numBins);
        tSur                = NaN(size(uniqueCues, 1), params.nSur);
        permRank            = NaN(size(uniqueCues));
        pPerm               = NaN(size(uniqueCues));
        pRanksum            = NaN(size(uniqueCues));
        considerRanksum     = false(size(uniqueCues));
        for iCue = 1:numel(uniqueCues)

            %% get cue periods and firing rates

            % index for cue periods
            isCue{iCue, 1}                  = contains(cueImgNameFull, uniqueCues{iCue});

            % firing rates
            cueFR{iCue, 1}                  = FR(isCue{iCue, 1}, :);

            % smoothed firing rates
            cueSmFR                         = smFR(isCue{iCue, 1}, :);

            %% cluster-based permutation test

            % compute test statistic
            [t(iCue, 1), isMax(iCue, :)]    = TG_ComputeStatistic_20251013(smFR, isCue{iCue, 1}, params);

            % compute surrogate test statistics
            for iSur = 1:params.nSur

                % values for random shifts of each cue period
                randShifts                      = randi(params.numBins, [sum(isCue{iCue, 1}), 1]);

                % compute new bin indices
                binIdx                          = mod((0:params.numBins - 1) - randShifts, params.numBins) + 1;

                % stimulus indices for all bins
                stimIdx                         = repmat((1:sum(isCue{iCue, 1}))', 1, params.numBins);

                % use linear indexing to extract shifted values
                surCueSmFR                      = cueSmFR(sub2ind([sum(isCue{iCue, 1}), params.numBins], stimIdx, binIdx));

                % surrogate firing rates
                surSmFR                         = smFR;
                surSmFR(isCue{iCue, 1}, :)      = surCueSmFR;
                
                % compute surrogate test statistic
                [tSur(iCue, iSur), ~]           = TG_ComputeStatistic_20251013(surSmFR, isCue{iCue, 1}, params);
            end

            % compute rank of empirical t-value in surrogat t-values
            permRank(iCue, 1)               = sum(t(iCue, 1) > tSur(iCue, :)) / params.nSur;

            % correct rank
            if (sum(any(cueFR{iCue, 1}(:, params.isStimBin) > 0, 2)) / sum(isCue{iCue, 1})) < params.minFractionActiveTrials
                permRank(iCue, 1)               = 0;
            end

            % p-value
            pPerm(iCue, 1)                      = 1 - permRank(iCue, 1);

            % Bonferroni correction
            if params.bonferroniCorrection
                pPerm(iCue, 1)                      = pPerm(iCue, 1) * size(unique(cueImgName), 1);
                if pPerm(iCue, 1) > 1
                    pPerm(iCue, 1) = 1;
                end
            end

            %% binwise ranksum test

            % calculate binwise ranksum
            [pRanksum(iCue, 1), considerRanksum(iCue, 1), ~] = binwise_ranksum(...
                cellfun(@(x) x * 1000, spikeTimes(isCue{iCue, 1}, :), 'Uni', 0), ...
                cellfun(@(x) x * 1000, spikeTimes, 'Uni', 0), ...
                [params.timeBaselineOn * 1000, params.timeBaselineOff * 1000], ...
                [params.timeStimOn * 1000, params.timeStimOff * 1000], ...
                100, params.alphaLevel, params.minFractionActiveTrials, true, [], 0.6, false);
        end

        %% test for significant response

        % permutation test
        significantResponse         = pPerm < params.alphaLevel;
        isConceptCell               = any(significantResponse(1:2:end) & significantResponse(2:2:end));
        isItemCell                  = any(significantResponse) & ~isConceptCell;

        %% create figure

        % figure
        if params.createFigure
            responseFigure      = figure('Units', 'normalized', 'Position', [0, 0, 1, 1], 'Visible', 'off');

            % create axes for all stimulus responses
            axSpikes            = NaN(size(uniqueCues));
            axFR                = NaN(size(uniqueCues));
            axHist              = NaN(size(uniqueCues));
            nAxes               = numel(uniqueCues) / 2 + 2;

            %% density plot

            % spike shapes
            thisSpikeShapes     = thisUnit.waveforms{:};

            % density plot
            axes('Position', [0.03, 0.4, 1/nAxes, 0.3]);
            out = TG_DensityPlot(((0:1:(size(thisSpikeShapes, 1) - 1)) / microSr) * 1000, thisSpikeShapes'); % convert to milliseconds
            ylim([out.lbound, out.ubound]);
            yticks([out.lbound, out.ubound]);
            xlabel('Time (ms)');
            ylabel('Voltage (µV)');
            tl  = title(thisLabel);
            set(gca, 'FontSize', 10);
            set(tl, 'FontSize', 12);

            % loop through cues
            for iCue = 1:numel(uniqueCues)

                %% this cue name

                % extract name
                thisCueName            = uniqueCues{iCue, 1};
                thisCueName            = strsplit(thisCueName, '_');
                thisCueName            = [thisCueName{2}, ' ', thisCueName{4}];

                %% raster plot

                % axis
                if mod(iCue, 2)
                    axSpikes(iCue)      = axes('Position', [ceil(iCue / 2)/nAxes + 1/nAxes, 0.82, 0.8/nAxes, 0.15]);
                else
                    axSpikes(iCue)      = axes('Position', [ceil(iCue / 2)/nAxes + 1/nAxes, 0.32, 0.8/nAxes, 0.15]);
                end

                % plot spikes
                thisCueSpikeTimes       = spikeTimes(isCue{iCue, 1}, :);
                for iTrial = 1:size(thisCueSpikeTimes, 1)

                    % plot horizontal lines for each spike
                    yVal                    = iTrial * ones(size(thisCueSpikeTimes{iTrial, 1}));
                    for iSpike = 1:size(thisCueSpikeTimes{iTrial, 1}, 1)
                        line([thisCueSpikeTimes{iTrial, 1}(iSpike), thisCueSpikeTimes{iTrial, 1}(iSpike)], [yVal(iSpike) - 0.4, yVal(iSpike) + 0.4], 'Color', [0, 0, 0, 0.7], 'LineWidth', 1);
                    end
                end

                % stimulus onset
                xline(params.timeStimOn, 'Color', [1, 0.2, 0, 0.7], 'LineWidth', 1, 'LineStyle', '-');
                axis tight;
                xlim([params.timeBaselineOn, params.timeStimOff]);

                % settings
                set(axSpikes(iCue), 'YDir', 'reverse', 'Box', 'off', 'TickDir', 'out', 'YTick', [], 'XTick', [], 'XColor', 'none', 'YColor', 'none');
                colormap(axSpikes(iCue), repmat([1; linspace(0.5, 0, 255)'], 1, 3));
                ylim([0, size(cueFR{iCue, 1}, 1) + 1]);
                if iCue == 1
                    set(gca, 'YColor', 'k');
                    ylabel('Stimulus');
                end
                tl = title(thisCueName, 'Interpreter', 'none');
                set(axSpikes(iCue), 'FontSize', 10);
                set(tl, 'FontSize', 12);

                %% firing rate plot

                % axis
                if mod(iCue, 2)
                    axFR(iCue)        = axes('Position', [ceil(iCue / 2)/nAxes + 1/nAxes, 0.7, 0.8/nAxes, 0.1]);
                else
                    axFR(iCue)        = axes('Position', [ceil(iCue / 2)/nAxes + 1/nAxes, 0.2, 0.8/nAxes, 0.1]);
                end
                hold on;
                TG_ShadeSEM_20250317(params.timeCenters, smFR(isCue{iCue, 1}, :), [0, 0, 0], 0.5);
                xline(params.timeStimOn, 'Color', [1, 0.2, 0, 0.7], 'LineWidth', 1, 'LineStyle', '-');
                scatter(axFR(iCue), params.timeCenters(isMax(iCue, :)), mean(smFR(isCue{iCue, 1}, isMax(iCue, :))), 'pentagram', 'filled', 'CData', [1, 0, 0]);
                set(gca, 'tickDir', 'out', 'box', 'off', 'YColor', 'none');
                if iCue == 1
                    set(gca, 'YColor', 'k');
                    xlabel('Time (s)');
                    ylabel('Firing rate (Hz)');
                end
                set(gca, 'FontSize', 10);

                % surrogate and empirical t-value plot
                if mod(iCue, 2)
                    axHist(iCue)        = axes('Position', [ceil(iCue / 2)/nAxes + 1/nAxes, 0.55, 0.8/nAxes, 0.08]);
                else
                    axHist(iCue)        = axes('Position', [ceil(iCue / 2)/nAxes + 1/nAxes, 0.05, 0.8/nAxes, 0.08]);
                end
                histogram(tSur(iCue, :), params.nSurHistBins, 'FaceColor', [0.5, 0.5, 0.5], 'FaceAlpha', 1);
                set(gca, 'tickDir', 'out', 'box', 'off', 'YColor', 'none');
                xline(t(iCue, 1), 'Color', 'r', 'LineWidth', 2);
                if iCue == 1
                    set(gca, 'YColor', 'k');
                    xlabel('Surrrogate t-values');
                    ylabel('Number of surrogates');
                end
                set(gca, 'FontSize', 10);
            end

            % link axes
            linkaxes([axSpikes, axFR], 'x');
            linkaxes(axFR, 'y');
            linkaxes(axHist, 'xy');

            % limits of firing rate axis
            yMaxFR          = max(cell2mat(get(axFR, 'YLim')), [], 'all');
            yMaxFR          = ceil(yMaxFR / 5) * 5;
            set(axFR, 'YLim', [0, yMaxFR], 'YTick', [0, yMaxFR]);

            % limits of surrogate histogram axis
            yMaxHist        = max(cell2mat(get(axHist, 'YLim')), [], 'all');
            yMaxHist        = ceil(yMaxHist / 1000) * 1000;
            set(axHist, 'YLim', [0, yMaxHist], 'YTick', [0, yMaxHist]);

            % plot p-values
            for iCue = 1:numel(uniqueCues)

                % plot p-value
                tPerm       = title(axHist(iCue, 1), sprintf('P_{perm} = %.3f', pPerm(iCue, 1)), 'FontSize', 10, 'FontWeight', 'normal');

                % set color
                if pPerm(iCue, 1) < params.alphaLevel

                    % red color
                    tPerm.Color     = [1, 0, 0];

                    % red rectangle
                    xL              = get(axSpikes(iCue), 'XLim');
                    yL              = get(axSpikes(iCue), 'YLim');
                    patch('Parent', axSpikes(iCue), 'XData', [xL(1), xL(2), xL(2), xL(1)], ...
                        'YData', [yL(1), yL(1), yL(2), yL(2)], 'EdgeColor', 'red', ...
                        'FaceColor', 'none', 'LineWidth', 1.5);
                else
                    tPerm.Color     = [0, 0, 0];
                end
            end

            %% save figure

            % save item- or wordselective cells
            if isItemCell
                exportgraphics(responseFigure, fullfile(savePath, 'ItemResponsiveCells', ...
                    strcat(extractBefore(sessions(iSess).name, '_'), '_Unit_', sprintf('%03d', thisUnit.id), '.jpg')));
            end

            % save concept cells
            if isConceptCell
                exportgraphics(responseFigure, fullfile(savePath, 'ConceptCells', ...
                    strcat(extractBefore(sessions(iSess).name, '_'), '_Unit_', sprintf('%03d', thisUnit.id), '.jpg')));
                exportgraphics(responseFigure, fullfile(paths.save, 'ConceptCells', ...
                    strcat(extractBefore(sessions(iSess).name, '_'), '_Unit_', sprintf('%03d', thisUnit.id), '.jpg')));
            end

            % close figure
            close(responseFigure);
        end

        %% collect results for this unit

        % basics
        unitRes                     = [];
        unitRes.subjectID           = subjectAndSession(1, 1);
        unitRes.sessionID           = subjectAndSession(1, 2);
        unitRes.unitID              = thisUnit.id;
        unitRes.brainRegion         = brainRegion;
        unitRes.cues                = uniqueCues';

        % permutation test results
        unitRes.maxTval             = t';
        unitRes.rankPermutationTest = permRank';

        % ranksum p-values
        unitRes.pValueRanksum       = pRanksum';
        unitRes.considerRanksum     = considerRanksum';

        % significant response
        unitRes.isConceptCell       = isConceptCell;

        % collapse across units
        sessRes(iUnit, :)           = unitRes;
    end

    % collect results across sessions
    allRes{iSess, 1}            = sessRes;
end

% unnest result cells
allRes  = cat(1, allRes{:});

% save output
save(fullfile(paths.save, 'allResults.mat'), 'allRes', '-v7.3');

%==========================================================================
% example units
%==========================================================================

% load previously saved output
r   = load(fullfile(paths.save, 'allResults.mat'));
s   = load(fullfile(paths.save, 'settings.mat'));
fprintf('Total number of cells: %d.\n', size(r.allRes, 1));

%% create concept cell example figure

% example cells
exampleConceptCells = ...
    [1, 2, 9, 5; 1, 2, 41, 5; 1, 3, 12, 1; ...
    1, 3, 29, 6; 4, 1, 9, 6; 6, 1, 22, 6; ...
    8, 2, 7, 6; 12, 2, 39, 4; 16, 1, 78, 2; ...
    16, 2, 2, 1; 16, 2, 46, 5; 16, 2, 49, 1; ...
    18, 2, 29, 1; 18, 2, 64, 7; 18, 2, 67, 0];

% example concept cell figure
exampleConceptFig      = figure('Units', 'centimeters', 'Position', [5, 5, 18, 18.5], ...
    'DefaultAxesTickDir', 'out', 'DefaultAxesTickDirMode','manual', 'DefaultAxesBox', 'off');

% figure content
TG_CreateExamplesFigure_20251016(exampleConceptFig, s, exampleConceptCells);

% save example figure
exportHybridFigure(exampleConceptFig, fullfile(paths.save, 'ConceptCellExamples_20251015.jpg'), fullfile(paths.save, 'ConceptCellExamples_20251015.svg'), 600);

%% create image- and word response example figure

% example cells
exampleResponsiveCells  = ...
    [1, 1, 0, 4; 1, 1, 50, 0; 1, 2, 3, 4; ...
    1, 2, 15, 3; 1, 3, 6, 5; 3, 1, 67, 0; ...
    3, 1, 75, 4; 3, 2, 80, 5; 3, 3, 51, 2; ...
    4, 3, 20, 2; 16, 2, 59, 6; 16, 2, 61, 5; ...
    8, 2, 8, 0; 12, 1, 51, 0; 15, 1, 9, 5];

% example concept cell figure
exampleResponseFig      = figure('Units', 'centimeters', 'Position', [5, 5, 18, 18.5], ...
    'DefaultAxesTickDir', 'out', 'DefaultAxesTickDirMode','manual', 'DefaultAxesBox', 'off');

% figure content
TG_CreateExamplesFigure_20251016(exampleResponseFig, s, exampleResponsiveCells);

% save example figure
exportHybridFigure(exampleResponseFig, fullfile(paths.save, 'ImageWordCellExamples_20251015.jpg'), fullfile(paths.save, 'ImageWordCellExamples_20251015.svg'), 600);

%% create overview of concept cells and item-responsive cells

% overview figure
overviewFig     = figure('Units', 'centimeters', 'Position', [5, 5, 18, 13.7], ...
    'DefaultAxesTickDir', 'out', 'DefaultAxesTickDirMode','manual', 'DefaultAxesBox', 'off');

% figure content
TG_CreateResponseOverviewFigure_20251105(overviewFig, s, r);

% save overview figure
exportgraphics(overviewFig, fullfile(paths.save, 'CellResponsesOverview_20251015.svg'), 'ContentType', 'Vector');