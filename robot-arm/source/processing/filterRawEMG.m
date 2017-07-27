function LinearEnvelope = filterRawEMG(raw_data, frequency, lower_cutoff, upper_cutoff)
% This function filters a raw EMG signal. Optional arguments are
% {frequency, lower_cutoff, upper_cutoff}. Frequency is the frequency at
% which the EMG signal was recorded, while the lower and upper cutoffs are
% for use in the Bandpass filter. 
%
% By default these arguments are set to [100, 3, 30], for use in the
% non-realtime implementation of the 1DOF Robot Arm at ATR. 

%% Deprecated code for option arguments. Keeping it for reference.
% % Check that too many input arguments haven't been supplied.
% numvarargs = length(varargin);
% if numvarargs > 3
%     error('filterRawEMG accepts at most 2 additional optional inputs.');
% end

% % Set defaults for optional inputs.
% optargs = {100 3 30};
% 
% % Overwrite the defaults if optional arguments are specified.
% [optargs{1:numvarargs}] = varargin{:};
% 
% % Create sensical variable names for the arguments.
% [frequency, lower_cutoff, upper_cutoff] = optargs{:};

%% Perform filtering.
% Filter.
BPFiltEMGPointsAll = ZeroLagButtFiltfilt(...
    (1/frequency), [lower_cutoff,upper_cutoff], 2, 'bp', raw_data);

% Rectify.
RectBPFiltEMGPointsAll = abs(BPFiltEMGPointsAll);

% Filter again to obtain the raw EMG envelope. 
LinearEnvelope = ZeroLagButtFiltfilt((1/frequency), 6, 2, 'lp', RectBPFiltEMGPointsAll);

end