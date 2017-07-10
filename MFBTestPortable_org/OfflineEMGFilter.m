%% Testing filtering of the EMG signal. 

% Load the EMG data. 
load('test3.mat');
emg_data = ad1(1:end,9);

% Set cutoffs. 
low_freq = 2;
high_freq = 99;

% Set sampling frequency.
sampling_frequency = 100;

% Nyquist Frequency - 1/2 Sampling frequency.
nyquist_frequency = sampling_frequency/2;

% Set up coefficients of Butterworth filter.
order = 6;
cutoff_frequencies = [low_freq high_freq]/sampling_frequency;
[b,a]=butter(order,cutoff_frequencies);

% Eliminate phase shift by filtering forward and backwards. 
filtered_emg_data=filtfilt(b,a,emg_data);