%% Run all EMG data processing scripts with one command. 
% A required argument decides whether saved settings for the offline or online 
% implementation should be used. Optionally, these arguments can be
% specified.
function runEMGScripts(data, freq, low, high)

% Parse input arguments & determine mode.
if nargin == 1
    freq = 200;
    low = 6;
    high = 80;
elseif nargin ~= 4
    error('runScripts requires precisely 1 or 4 arguments');
end

% Get the correct path to the data depending on the mode. 
datapath = [getenv('xor2') filesep data filesep];

% Declare the file to be loaded.
files = {[datapath data]};

% Process the raw EMG data.
processed_emg = processRawData(files,mode,freq,low,high);

% Due to difficulties in settings up real-time feedback, some changes were
% necessary for the averageEMGEnvelopes script in the online case. 
averaged_waveforms = averageOnlineEMGEnvelopes(processed_emg);

end