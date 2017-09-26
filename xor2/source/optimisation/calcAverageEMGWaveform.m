function [raw_emg, processed_emg, averaged_waveforms ] = ...
    calcAverageEMGWaveform(data, peaks, channels, lrange, urange)
% This is basically the quantitative component of evaluateEMGResults,
% but I wanted more convenient access to this.

n_channels = size(channels,2);

raw_emg{1,n_channels} = [];
averaged_waveforms{1,n_channels} = {};
processed_emg{1,n_channels} = {};
for i=1:n_channels
    raw_emg{1,i} = data(lrange:urange,channels(1,i));
    processed_emg{1,i} = filterRawEMG(data(lrange:urange,channels(1,i)));
    averaged_waveforms{1,i} = averageEMGEnvelopes(processed_emg{1,i},peaks);
end


end

