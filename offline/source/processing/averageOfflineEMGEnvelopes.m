%% Function to get an 'average EMG envelope' for each case. 
% Assumed we have access to a generated_ref_traj.mat file and 
% filtered_emg_bicep data. Returns a cell array waveforms of averaged waveforms. 
function averaged_waveforms = averageOfflineEMGEnvelopes(filtered_emg_bicep)

% Import the generated reference trajectory. 
load([getenv('ATR_HOME') filesep 'reference' filesep 'generated_ref_traj.mat']);

% Identify the start of each oscillation. Add 150 to start as this is the
% end of the stationary '0' part of the reference trajectory. 
oscillations = 150;
for i=1:size(generated_ref_traj,1)
    if i > 150 && generated_ref_traj(i) == 0
        oscillations = [oscillations i];
    end
end
% This gives 8 results, so 7 full oscillations going from 1 to the next (
% we can't assume the last one gives a full oscillation). There were also
% some issues with the first one (as can be seen from the raw counter), so
% we will ignore this also. So we will average over the 6 middle waveforms.

% Create cell arrays to store each waveform. Note, order is end passive,
% end active, mid passive, mid active, base passive, base active - for
% rows. Columns gives an individual waveform.
waveforms{6,6} = {};

% Note: order is end passive, end active, mid passive, mid active, base
% passive, base, active. 
for i=2:7
    for j=1:6
        waveforms{j,i-1} = filtered_emg_bicep{1,j}(oscillations(i):oscillations(i+1)-1);
    end
end

% Average the waveforms for each context.
averaged_waveforms{6} = {};
for i=1:6
    averaged_waveforms{i} = (waveforms{i,1} ...
        + waveforms{i,2} ...
        + waveforms{i,3} ...
        + waveforms{i,4} ...
        + waveforms{i,5} ...
        + waveforms{i,6})/6;
end

end
    