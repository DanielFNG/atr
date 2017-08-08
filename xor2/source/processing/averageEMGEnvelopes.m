%% Function to get an 'average EMG envelope' for each case. 
% Assumed we have access to a generated_ref_traj.mat file and 
% filtered_emg_bicep data. Returns a cell array waveforms of averaged waveforms. 
function averaged_waveforms = averageEMGEnvelopes(processed_emg)

% Import the generated reference trajectory. 
load([getenv('xor2') filesep 'reference' filesep 'measured_ref_traj.mat']);

% Identify the start of each oscillation for the active cases only!
oscillations = 150;
for i=1:size(measured_ref_traj,1)
    if i > 150 && measured_ref_traj(i) == 0
        oscillations = [oscillations i];
    end
end
% This gives 8 results, so 7 full oscillations going from 1 to the next (
% we can't assume the last one gives a full oscillation). So we will average 
% over the first 7 waveforms. This doesn't actually affect the passive case
% since I identified these peaks separately but oh well. 

% Create cell arrays to store each waveform. Note, order is end passive,
% end active, mid passive, mid active, base passive, base active - for
% rows. Columns gives an individual waveform.
waveforms{6,7} = {};

% Note: order is end passive, end active, mid passive, mid active, base
% passive, base, active. 
for i=1:7
    for j=2:2:6
        waveforms{j,i} = processed_emg{1,j}(oscillations(i):oscillations(i+1)-1);
    end
    for j=1:2:5
        waveforms{j,i} = processed_emg{1,j}(passive_peaks{j}(i):passive_peaks{j}(i+1)-1);
    end
end

% Average the waveforms for each context.
averaged_waveforms{6} = {};
for i=1:6
    if i ~= 3
        averaged_waveforms{i} = (stretchVector(waveforms{i,1},200) ...
            + stretchVector(waveforms{i,2},200) ...
            + stretchVector(waveforms{i,3},200) ...
            + stretchVector(waveforms{i,4},200) ...
            + stretchVector(waveforms{i,5},200) ...
            + stretchVector(waveforms{i,6},200) ...
            + stretchVector(waveforms{i,7},200))/7;
    else
        averaged_waveforms{i} = (stretchVector(waveforms{i,1},200) ...
            + stretchVector(waveforms{i,3},200) ...
            + stretchVector(waveforms{i,4},200) ...
            + stretchVector(waveforms{i,5},200) ...
            + stretchVector(waveforms{i,6},200) ...
            + stretchVector(waveforms{i,7},200))/6;
    end
end

end
    