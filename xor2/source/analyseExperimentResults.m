function analyseExperimentResults(file_name, folder_name)
% Calculate the objective function (defined herein) for data saved in
% [save_name '.mat'], located in the data folder. 

% Create path to the input data. 
if nargin == 2
    save_name = [folder_name filesep file_name];
elseif nargin == 1
    save_name = file_name;
else
    error('Incorrect number of inputs.');
end
    
% EMG channels.
channels = [1];

% Indices for the assistance stage of the experiment, post-training.
lrange = 8000; 
urange = 12000;

% Indices describing the start/end of each waveform in the region of 
% interest according to the reference trajectory. This has been 
% pre-calculated. Since we pass data in the range (lrange:urange), which 
% then becomes stored as 1:(urange-lrange), we subtract (lrange-1) from 
% raw_peaks to get the adjusted peaks.
raw_peaks = [8184,8630,9076,9522,9968,10414,10860,11306,11752];
peaks = raw_peaks - (lrange - 1);

% Get data path and open file. 
data_folder = [getenv('XOR2') filesep 'data' filesep];
load([data_folder save_name '.mat']);

% Evaluate (qualitatively and quantitatively) the EMG results. Note that we 
% assume the EMG data is stored in a matrix with size (timesteps, channels) 
% called ad3. 

%processed_emg = evaluateEMGResults(ad3,peaks,channels,lrange,urange);

% Below: deprecated, computes average waveforms instead - but this isn't
% working well.
[raw_emg, processed_emg, averaged_waveforms] = ...
    evaluateEMGResults(ad3,peaks,channels,lrange,urange); 

% Calculate the result of the objective function. 
result = objectiveFunction(averaged_waveforms);

% Output the result to the screen so the experiment can continue.
fprintf('The objective function result was %f.\n', result);

% Save the result for posterity in [save_name '_result.mat'], along with the 
% processed_emg and averaged_waveforms for this case.
% save([data_folder save_name '_result.mat'], 'result', 'processed_emg', 'averaged_waveforms');
save([data_folder 'results' filesep save_name], ...
    'result', 'processed_emg', 'averaged_waveforms');

end

