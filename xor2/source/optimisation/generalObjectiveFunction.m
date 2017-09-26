function [result, terms] = ...
    generalObjectiveFunction(filename, x_coeff, y_coeff, z_coeff, mode)
% This is the general objective function as outlined in my ATR report which
% was used to analyse the data collected while walking with the XoR2
% exoskeleton.

% Channels used for the EMG sensors.
channels = [2,3]; % For shank experiment.
% channels = [1]; % For thigh experiment. 
% channels = [2,4]; % For non-spanning experiment. 
% Should double check that the above pre-sets are correct!

% Indices for the non-assistance stage of the experiment, post-training.
lrange_unassisted = 2000;
urange_unassisted = 6000;

% Indices for the assistance stage of the experiment, post-training.
lrange_assisted = 8000; 
urange_assisted = 12000;

% Load the correct file. In particular this gives us access to the 'ad3' 
% (EMG) and 'ad1' (encoder) arrays. 
load(filename);

% Indices describing the start/end of each waveform in the region of 
% interest according to the reference trajectory. This has been 
% pre-calculated. Since we pass data in the range (lrange:urange), which 
% then becomes stored as 1:(urange-lrange), we subtract (lrange-1) from 
% raw_peaks to get the adjusted peaks.
raw_peaks_unassisted = [2385,2833,3280,3725,4171,4615,5064,5510,5953];
peaks_unassisted = raw_peaks_unassisted - (lrange_unassisted - 1);

% As above for assisted case. 
raw_peaks_assisted = [8184,8630,9076,9522,9968,10414,10860,11306,11752];
peaks_assisted = raw_peaks_assisted - (lrange_assisted - 1);

% Calculate the average emg waveforms during assistance. 
[~, ~, avg_emg_assisted] = calcAverageEMGWaveform(...
    ad3, peaks_assisted, channels, lrange_assisted, urange_assisted);

% Calculate absolute total & peaks.
total = 0;
peak = 0;
n_assisted_waveforms = size(avg_emg_assisted,2);
for i=1:n_assisted_waveforms
    total = total + sum(avg_emg_assisted{1,i});
    peak = peak + max(avg_emg_assisted{1,i});
end

% Calculate absolute tracking error.
terr = computeTrackingError(angle0, reference, peaks_assisted);

% If relative, calculate during non-assist period.
if strcmp(mode, 'relative')
    % Calculate the average emg waveforms without assistance. 
    [~, ~, avg_emg_unassisted] = calcAverageEMGWaveform(...
        ad3, peaks_unassisted, channels, lrange_unassisted, ...
        urange_unassisted);
    
    % Calculate unassisted total and peaks.
    no_assist_total = 0;
    no_assist_peak = 0;
    n_unassisted_waveforms = size(avg_emg_unassisted,2);
    for i=1:n_unassisted_waveforms
        no_assist_total = no_assist_total + sum(avg_emg_unassisted{1,i});
        no_assist_peak = no_assist_peak + max(avg_emg_unassisted{1,i});
    end
        
    % Calculate unassisted tracking error.
    no_assist_terr = computeTrackingError(angle0, reference, ...
        peaks_unassisted);
    
    % Compute the relative result.
    result = x_coeff*(total - no_assist_total)/no_assist_total*100 + ...
        y_coeff*(peak - no_assist_peak)/no_assist_peak*100 + ...
        z_coeff*(terr - no_assist_terr)/no_assist_terr*100;
    
elseif strcmp(mode, 'absolute')
    no_assist_total = 'n/a';
    no_assist_peak = 'n/a';
    no_assist_terr = 'n/a';
    % Compute the absolute result. 
result = x_coeff*total + y_coeff*peak + z_coeff*terr;
else
    error('mode should be relative or absolute')
end

terms.mode = mode;
terms.total = total;
terms.peak = peak;
terms.terr = terr;
terms.no_assist_total = no_assist_total;
terms.no_assist_peak = no_assist_peak;
terms.no_assist_terr = no_assist_terr;

end

