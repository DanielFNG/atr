function averaged_waveforms = ...
    evaluateEMGResults(data, peaks, channels, lrange, urange)
% Qualitatively and quantitatively analyse EMG data. 

%% Parse inputs.
if nargin < 3 || nargin > 5 || nargin == 4
    error('Require 3 or 5 arguments.')
elseif nargin == 3
    lrange = 1;
    urange = size(data,1);
end

if isscalar(channels)
    n_channels = channels;
    channels = 1:channels;
else
    n_channels = size(channels,2);
end


%% Qualitative EMG analysis. 

% First it must pass a simple visual test to make sure nothing's gone wrong
% with the EMG! So we plot the raw EMG results for the region of interest. 
figure
for i=1:n_channels
    ax = subplot(n_channels,1,i);
    plot(ax,data(lrange:urange,channels(1,i)));
end

% Ask user whether or not the EMG looks good enough to continue. 
x = input(['If everything looks fine input ''y'' to continue. Otherwise, ' ...
    'input ''n''.']);
if strcmp(x,'y')
    display('Passed visual test. Moving on...');
else
    display('Failed visual test. Exiting objective function calculation.');
    return
end

%% Quantitative EMG analysis.

% Create cell arrays to hold the averaged waveform for each channel. 
averaged_waveforms{1,n_channels} = {};
for i=1:n_channels
    % Process the raw EMG. Defaults of [200,6,80] are assumed in filterRawEMG,
    % but these can alternatively be supplied as optional arguments.
    processed_emg = filterRawEMG(data(lrange:urange,channels(1,i)));
    %processed_emg{1,i} = filterRawEMG(data(lrange:urange,i), freq, low, high);
    
    % Average the processed EMG in to one waveform per channel.
    averaged_waveforms{1,i} = averageEMGEnvelopes(processed_emg, peaks);
end

end

