% Some definitions.
data_path = [getenv('XOR2') filesep 'data' filesep];
ref_path = [getenv('XOR2') filesep 'reference' filesep];
reference_data = 'collecting_reference_trajectories.mat';
data_bounds = [30000, 37000];
n_cycles = 200;

% Load the reference trajectory data. 
load([data_path reference_data]);

% Identify the gait cycles from the data at 1.5m on the Treadmill. 
[~, locs] = identifyGaitCycle(angle1, angle0, data_bounds);

% Calculate an average gait cycle given this data. 
avg_slices = averageSlices(angle1, angle0, locs);

% Create a trajectory from the average cycles. 
trajectory = createTrajectory(avg_slices, n_cycles);

% Save this as the reference trajectory. 
measured_ref_traj = trajectory;
save([ref_path 'measured_ref_traj.mat'], 'measured_ref_traj');

