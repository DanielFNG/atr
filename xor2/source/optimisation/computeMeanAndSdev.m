function result = computeMeanAndSdev(filename, channel, low_pass)

% Indices for the non-assistance stage of the experiment, post-training.
lrange_unassisted = 2000;
urange_unassisted = 6000;

% Indices for the assistance stage of the experiment, post-training.
lrange_assisted = 8000; 
urange_assisted = 12000;

% Load the correct file. In particular this gives us access to the 'ad3' 
% (EMG), 'ad1' (encoder) and 'time' (time) arrays. 
load(filename, 'ad3', 'time', 'angle0');

% Find the peaks to separate the EMG signals for the unassisted case.
[~, peaks_unassisted] = findpeaks(angle0(...
    lrange_unassisted + 150:urange_unassisted - 150, 2), ...
    'MinPeakDistance', 250, 'NPeaks', 8);
peaks_unassisted = peaks_unassisted + 150;

% As above for assisted case.
[~, peaks_assisted] = findpeaks(angle0(...
    lrange_assisted + 150:urange_assisted - 150, 2), ...
    'MinPeakDistance', 250, 'NPeaks', 8);
peaks_assisted = peaks_assisted + 150;

% Filter raw EMG then calculate the mean/sdev total EMG.
unassisted_time = time(lrange_unassisted:urange_unassisted);
assisted_time = time(lrange_assisted:urange_assisted);

unassisted_emg = ...
    filterRawEMG(ad3(lrange_unassisted:urange_unassisted, channel), 200, 2, low_pass);
assisted_emg = ...
    filterRawEMG(ad3(lrange_assisted:urange_assisted, channel), 200, 2, low_pass);
[result.unassisted.mean, result.unassisted.sdev] = avgTotalEMG(...
    unassisted_emg, unassisted_time, peaks_unassisted);
[result.assisted.mean, result.assisted.sdev] = avgTotalEMG(...
    assisted_emg, assisted_time, peaks_assisted);
[result.relative.mean, result.relative.sdev] = relativeAvgTotalEMG(...
    unassisted_emg, unassisted_time, peaks_unassisted, ...
    assisted_emg, assisted_time, peaks_assisted);

end


