%% Function to process raw EMG.
function filtered_emg_bicep = processRawData(files, mode, freq, low, high)
% Returns a cell array with processed EMG data for each datafile loaded in.

% Set up cell array to hold results.
filtered_emg_bicep{size(files,2)} = {}; 

% Filter the EMG for each set of raw data. Currently only bicep seems to
% have worked, so focusing on this for now. 
for i=1:size(files,2)
    load(files{i});
    if strcmp(mode, 'online')
        raw_emg_bicep = ad_mfb1(1:end,9);
    else
        raw_emg_bicep = ad1(1:end,9);
    end
    filtered_emg_bicep{i} = filterRawEMG(raw_emg_bicep, freq, low, high);
end

end