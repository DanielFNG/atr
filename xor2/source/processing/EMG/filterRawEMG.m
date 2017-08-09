function LinearEnvelope = filterRawEMG(raw_data, varargin)
% This function filters a raw EMG signal. Optional arguments are
% {frequency, lower_cutoff, upper_cutoff}. Frequency is the frequency at
% which the EMG signal was recorded, while the lower and upper cutoffs are
% for use in the Bandpass filter. 
%
% By default these arguments are set to [200, 6, 80], for use in the
% realtime implementation on the XoR2 Exoskeleton at ATR. 

% Check that too many input arguments haven't been supplied.
numvarargs = length(varargin);
if numvarargs > 3
    error('filterRawEMG accepts at most 3 additional optional inputs.');
end

% Set defaults for optional inputs.
optargs = {200 6 80};

% Overwrite the defaults if optional arguments are specified.
[optargs{1:numvarargs}] = varargin{:};

% Create sensical variable names for the arguments.
[frequency, lower_cutoff, upper_cutoff] = optargs{:};

%% Perform filtering.
% Filter.
BPFiltEMGPointsAll = ZeroLagButtFiltfilt(...
    (1/frequency), [lower_cutoff,upper_cutoff], 2, 'bp', raw_data);

% Rectify.
RectBPFiltEMGPointsAll = abs(BPFiltEMGPointsAll);

% Filter again to obtain the raw EMG envelope. 
LinearEnvelope = ZeroLagButtFiltfilt((1/frequency), 6, 2, 'lp', RectBPFiltEMGPointsAll);

end