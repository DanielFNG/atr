%% Function to get an 'average EMG envelope' for each case. 
% Returns an averaged waveform given some processed emg data and indices
% denoting the start/end of each wave. 
function average_waveform = averageEMGEnvelopes(processed_emg, peaks)

n_waves = size(peaks,1) - 1;
waveforms{1,n_waves} = {};

sizes = zeros(1,n_waves);
for i=1:n_waves
    sizes(1,i) = peaks(i+1) - peaks(i);
end
avg_size = round(mean(sizes),0);

for j=1:n_waves
    waveforms{1,j} = processed_emg(peaks(j):peaks(j+1)-1);
end

% Average the waveforms.
average_waveform = zeros(1,avg_size);
for j=1:n_waves
    average_waveform = average_waveform + stretchVector(waveforms{1,j},avg_size);
end
average_waveform = average_waveform/n_waves;

end
    