function [val, sdev] = avgTotalEMG(processed_emg, time, peaks)

n_waves = length(peaks) - 1;
measurements = zeros(n_waves,1);

% Compute the total EMG for each waveform.
for i=1:n_waves
    waveform = processed_emg(peaks(i):peaks(i+1)-1);
    times = time(peaks(i):peaks(i+1)-1);
    measurements(i,1) = trapz(times, waveform); 
end

% Return the mean and standard deviation. 
val = mean(measurements);
sdev = std(measurements);
 

