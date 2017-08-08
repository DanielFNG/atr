%% Function to process raw EMG.
function processed_emg = processRawData(file, freq, low, high)
% Returns processed EMG data as a 4-element cell array, one for each EMG 
% channel.

processed_emg{1,4} = {};

% Filter the EMG for each set of raw data. Currently only bicep seems to
% have worked, so focusing on this for now. 
load(file);
for i=1:4
    processed_emg{{1,i}} = filterRawEMG(ad1(1:end,8+i), freq, low, high);
end

end