function result = computeMeanAndSdev(filename, channel)

% Indices for the non-assistance stage of the experiment, post-training.
lrange_unassisted = 2000;
urange_unassisted = 6000;

% Indices for the assistance stage of the experiment, post-training.
lrange_assisted = 8000; 
urange_assisted = 12000;

% Load the correct file. In particular this gives us access to the 'ad3' 
% (EMG), 'ad1' (encoder) and 'time' (time) arrays. 
load(filename, 'ad3', 'time');

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

% Filter raw EMG then calculate the mean/sdev total EMG.
unassisted_time = time(lrange_unassisted:urange_unassisted);
assisted_time = time(lrange_assisted:urange_assisted);

unassisted_emg = ...
    filterRawEMG(ad3(lrange_unassisted:urange_unassisted, channel));
assisted_emg = ...
    filterRawEMG(ad3(lrange_assisted:urange_assisted, channel));
[result.unassisted.mean, result.unassisted.sdev] = avgTotalEMG(...
    unassisted_emg, unassisted_time, peaks_unassisted);
[result.assisted.mean, result.assisted.sdev] = avgTotalEMG(...
    assisted_emg, assisted_time, peaks_assisted);
[result.relative.mean, result.relative.sdev] = relativeAvgTotalEMG(...
    unassisted_emg, unassisted_time, peaks_unassisted, ...
    assisted_emg, assisted_time, peaks_assisted);

end


