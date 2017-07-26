%% Run all EMG data processing scripts with one command. 
% A required argument decides whether saved settings for the offline or online 
% implementation should be used. Optionally, these arguments can be
% specified.
function runScripts(mode, freq, low, high)

% Parse input arguments & determine mode.
if nargin == 1
    if strcmp(mode, 'offline')
        freq = 100;
        low = 3;
        high = 30;
    elseif strcmp(mode, 'online')
        freq = 250;
        low = 6;
        high = 100;
    else
        error('mode should be offline or online');
    end
elseif nargin ~= 4
    error('runScripts requires precisely 1 or 4 arguments');
end

% Get the correct path to the data depending on the mode. 
base = [getenv('ATR_HOME') filesep];
if strcmp(mode, 'offline')
    datapath = [base 'offline' filesep 'data' filesep];
elseif strcmp(mode, 'online')
    datapath = [base 'online' filesep 'data' filesep];
else
    error('mode should be offline or online')
end

% Declare the files to be loaded.
files = {[datapath 'end_passive.mat'], [datapath 'end_active.mat'], ...
    [datapath 'mid_passive.mat'], [datapath 'mid_active.mat'], ...
    [datapath 'base_passive.mat'], [datapath 'base_active.mat']};

% Declare labels for plotting.
labels = {'end-p', 'end-a', 'mid-p', 'mid-a', 'base-p', 'base-a'};

% Process the raw EMG data.
filtered_emg_bicep = processRawData(files,mode,freq,low,high);

% Due to difficulties in settings up real-time feedback, some changes were
% necessary for the averageEMGEnvelopes script in the online case. 
if strcmp(mode, 'offline')
    averaged_waveforms = averageOfflineEMGEnvelopes(filtered_emg_bicep);
else
    averaged_waveforms = averageOnlineEMGEnvelopes(filtered_emg_bicep);
end

% Plot the resulting data. 
plotResults(filtered_emg_bicep, averaged_waveforms,labels);

end