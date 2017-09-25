function result = generalObjectiveFunction(filename, x, y, z, mode)
% This is the general objective function as outlined in my ATR report which
% was used to analyse the data collected while walking with the XoR2
% exoskeleton. 

% Indices for the non-assistance stage of the experiment, post-training.
lrange_unassisted = 2000;
urange_unassisted = 6000;

% Indices for the assistance stage of the experiment, post-training.
lrange_assisted = 8000; 
urange_assisted = 12000;

% Indices describing the start/end of each waveform in the region of interest 
% according to the reference trajectory. This has been pre-calculated.
% Since we pass data in the range (lrange:urange), which then becomes stored as
% 1:(urange-lrange), we subtract (lrange-1) from raw_peaks to get the
% adjusted peaks.
raw_peaks_unassisted = []
peaks_unassisted = raw_peaks_unassisted - (lrange_unassisted - 1);

raw_peaks_assisted = [8184,8630,9076,9522,9968,10414,10860,11306,11752];
peaks_assisted = raw_peaks_assisted - (lrange_assisted - 1);

% If relative, calculate during non-assist period.
if strcmp(mode, 'relative')
    % Calculate total.
    % Calculate peaks.
    % Calculate tracking error.
elseif strcmp(mode, 'absolute')
    no_assist_total = 0;
    no_assist_peak = 0;
    no_assist_terr = 0;
else
    error('mode should be relative or absolute')
end

% Calculate during assist period... start with total.

% Calculate peaks.

% Calculate error.

% Combine in the requested way to form the overall objective function
% result.
result = x*(total - no_assist_total) ...
    + y*(peak - no_assist_peak) ...
    + z*(terr - no_assist_terr);

end

