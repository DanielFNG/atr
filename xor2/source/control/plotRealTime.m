function [time, hip_pos, time_taken] = plotRealTime(varargin)
% Function for real time plotting of a joint angle overlayed with a
% reference trajectory in real time. Currently configured for the right hip
% - if this is changed some settings in here will need to be changed.
%
% Function rather than script for easy modifying of exp time, frequency and
% the reference trajectory. Arguments are: (exp_time, exp_freq, ref), all
% are optional. 
%
% Reference trajectory, 'ref', should be given as the name of a Matlab save
% file in atr/xor2/reference without the '.mat' which should also be the name
% of the saved variable, following convention. 
% i.e. ref = ref_traj, points to ref_traj.mat in atr/xor2/reference, which 
%      has the variable 'ref_traj' saved. 

%% Handle input variables and defaults.
% Require the correct number of inputs.
numvarargs = length(varargin);
if numvarargs > 3
    error('plotRealTime accepts at most 2 additional optional inputs.');
end

% Set defaults for optional inputs. 
% [exp_time freq ref]
optargs = {60 200 'measured_ref_traj'};

% Overwrite the defaults if optional arguments are specified.
[optargs{1:numvarargs}] = varargin{:};

% Create sensical variable names for the arguments.
[exp_time, exp_freq, ref] = optargs{:};

%% Setup
% Experimental details and parameters.
fpp = 5; % if this variable is to be changed the realtime .py control code has 
         % to be changed also!
timestep = 1/exp_freq;
n_frames = exp_freq * exp_time;
leg = 1; % right
joint = 3; % hip

% Create arrays to store data, and some parameters for in-loop logic.
time = zeros(n_frames/fpp,1);
hip_pos = zeros(n_frames/fpp,1);
j = 1;
k = 1;

% Load or use the reference trajectory.
data = load([getenv('ATR_HOME') filesep 'xor2' filesep 'reference' filesep ref '.mat']);
ref_traj = data.(ref);

% Open a TCP/IP server & wait for connection.
disp('This function will plot data in realtime to the screen.')
fprintf('Input data is at %u Hz.\n', exp_freq);
fprintf('Data will be plotted at %u Hz.\n', exp_freq/5);
disp('Opening server connection...')
t = tcpip('0.0.0.0', 10003, 'NetworkRole', 'server');
t.InputBufferSize = 12; % 5/6 digits from time and 7/6 digits from angle
fopen(t);
disp('Client connected.')

% Prepare figure for plotting.
f = figure('Name', 'Realtime Plot');
plot(0:timestep:(exp_time-timestep),ref_traj(1:n_frames,leg,joint))
axis([0,2.5,-1,0.4]); % Configured for roughly one gait cycle for right hip.
axis manual
hold on
movegui('northwest');
drawnow

%% Begin looping and collecting data. 
% i = 1 - await data, start timer and create plot line 
disp('Awaiting data stream...')
data=char(fread(t,t.InputBufferSize));
disp('Data received.')
tic;
time(1,1)=str2double(data(1:5)');
hip_pos(1,1)=str2double(data(6:t.InputBufferSize)');
y = plot([time(1,1)],[hip_pos(1,1)]);
drawnow limitrate

% i = 6,11,16...450 - plot but don't update plot axes 
for i=(1+fpp):fpp:450
    index = (i + 4 * mod(i,fpp))/fpp;
    data=char(fread(t,t.InputBufferSize));
    time(index,1)=str2double(data(1:5)');
    hip_pos(index,1)=str2double(data(6:t.InputBufferSize)');
    y.XData = time(1:index,1);
    y.YData = hip_pos(1:index,1);
    drawnow limitrate
end

% For i=451:5:2001... up to 10s. - start to update plot axes.
for i=451:fpp:2001
    index = (i + 4 * mod(i,fpp))/fpp;
    data=char(fread(t,t.InputBufferSize));
    time(index,1)=str2double(data(1:5)');
    hip_pos(index,1)=str2double(data(6:t.InputBufferSize)');
    k = k + 1;
    y.XData = time(k:index,1);
    y.YData = hip_pos(k:index,1);
    j = j + fpp;
    axis([0 + (j-1)*timestep,2.5 + (j-1)*timestep,-1,0.4]);
    drawnow limitrate
end

% i = 2006,..., upperlimit - when time is more than 10s adjust for the
% extra digit it takes up. 
upper_limit = n_frames - mod(n_frames, fpp);
for i=2006:fpp:upper_limit
    index = (i + 4 * mod(i,fpp))/fpp;
    data=char(fread(t,t.InputBufferSize));
    time(index,1)=str2double(data(1:6)');
    hip_pos(index,1)=str2double(data(7:t.InputBufferSize)');
    k = k + 1;
    y.XData = time(k:index,1);
    y.YData = hip_pos(k:index,1);
    j = j + fpp;
    axis([0 + (j-1)*timestep,2.5 + (j-1)*timestep,-1,0.4]);
    drawnow limitrate
end
time_taken = toc;

%% Close the connection, figure and finish.. 
fclose(t);
display('Experiment complete.');
fprintf('Displayed %f seconds of data in %f seconds.\n', ...
    time(end,1) - time(1,1), time_taken);

end