function [val, sdev] = relativeAvgTotalEMG(...
    unassisted_emg, unassisted_time, unassisted_peaks, ...
    assisted_emg, assisted_time, assisted_peaks)

n_waves = length(unassisted_peaks) - 1;
measurements = zeros(n_waves*n_waves,1);

% Compute the total EMG for each assisted waveform with EACH unassisted 
% waveform.
for i=1:n_waves
    for j=1:n_waves
        unassisted_waveform = ...
            unassisted_emg(unassisted_peaks(i):unassisted_peaks(i+1)-1);
        unassisted_times = ...
            unassisted_time(unassisted_peaks(i):unassisted_peaks(i+1)-1);

        assisted_waveform = ...
            assisted_emg(assisted_peaks(j):assisted_peaks(j+1)-1);
        assisted_times = ...
            assisted_time(assisted_peaks(j):assisted_peaks(j+1)-1);

        measurements(j + (i-1)*n_waves, 1) = ...
            100*(trapz(unassisted_times, unassisted_waveform) - ...
            trapz(assisted_times, assisted_waveform)) / ...
            trapz(unassisted_times, unassisted_waveform);
    end
end

% Return the mean and standard deviation. 
val = mean(measurements);
sdev = std(measurements);