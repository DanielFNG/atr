%% Script to create the ground truth graphs. 

% Paths to the data files.
path_shank = [getenv('XOR2') filesep 'data' filesep 'shank_span'];
path_thigh = [getenv('XOR2') filesep 'data' filesep 'span'];

% Files in each case.
files_shank = dir(path_shank);
files_thigh = dir(path_thigh);

% Correct channels.
thigh_channel = [4];
shank_channel = [1];

% The measurement order and position order in each case. 
thigh_measurement_order = ...
    [6,11,19,5,15,20,16,18,8,9,14,10,23,13,12,17,21,4,7,22,3];
thigh_position_order = ...
    [3,4,5,6,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,7];
shank_measurement_order = [3,7,8,13,4,14,10,11,5,9,15,12];
shank_position_order =    [3,4,8,9,10,11,12,13,14,15,5,7];

% First generate arrays holding the results for the thigh. 
thigh.measurement.total = zeros(1,size(thigh_measurement_order,2));
thigh.measurement.peak = zeros(1,size(thigh_measurement_order,2));
thigh.measurement.terr = zeros(1,size(thigh_measurement_order,2));
thigh.measurement.all = zeros(1,size(thigh_measurement_order,2));

thigh.position.total = zeros(1,size(thigh_measurement_order,2));
thigh.position.peak = zeros(1,size(thigh_measurement_order,2));
thigh.position.terr = zeros(1,size(thigh_measurement_order,2));
thigh.position.all = zeros(1,size(thigh_measurement_order,2));

for i=1:size(thigh_measurement_order,2)
    thigh.measurement.total(1,i) = generalObjectiveFunction([path_thigh filesep files_thigh(thigh_measurement_order(i)).name],1,0,0,'relative',thigh_channel);
    thigh.measurement.peak(1,i) = generalObjectiveFunction([path_thigh filesep files_thigh(thigh_measurement_order(i)).name],0,1,0,'relative',thigh_channel);
    thigh.measurement.terr(1,i) = generalObjectiveFunction([path_thigh filesep files_thigh(thigh_measurement_order(i)).name],0,0,1,'relative',thigh_channel);
    thigh.measurement.all(1,i) = generalObjectiveFunction([path_thigh filesep files_thigh(thigh_measurement_order(i)).name],1,1,1,'relative',thigh_channel);

    thigh.position.total(1,i) = generalObjectiveFunction([path_thigh filesep files_thigh(thigh_position_order(i)).name],1,0,0,'relative',thigh_channel);
    thigh.position.peak(1,i) = generalObjectiveFunction([path_thigh filesep files_thigh(thigh_position_order(i)).name],0,1,0,'relative',thigh_channel);
    thigh.position.terr(1,i) = generalObjectiveFunction([path_thigh filesep files_thigh(thigh_position_order(i)).name],0,0,1,'relative',thigh_channel);
    thigh.position.all(1,i) = generalObjectiveFunction([path_thigh filesep files_thigh(thigh_position_order(i)).name],1,1,1,'relative',thigh_channel);
end

% Now generate arrays holding the results for the shank. 
shank.measurement.total = zeros(1,size(shank_measurement_order,2));
shank.measurement.peak = zeros(1,size(shank_measurement_order,2));
shank.measurement.terr = zeros(1,size(shank_measurement_order,2));
shank.measurement.all = zeros(1,size(shank_measurement_order,2));

shank.position.total = zeros(1,size(shank_measurement_order,2));
shank.position.peak = zeros(1,size(shank_measurement_order,2));
shank.position.terr = zeros(1,size(shank_measurement_order,2));
shank.position.all = zeros(1,size(shank_measurement_order,2));

for i=1:size(shank_measurement_order,2)
    shank.measurement.total(i) = generalObjectiveFunction([path_shank filesep files_shank(shank_measurement_order(i)).name],1,0,0,'relative',shank_channel);
    shank.measurement.peak(i) = generalObjectiveFunction([path_shank filesep files_shank(shank_measurement_order(i)).name],0,1,0,'relative',shank_channel);
    shank.measurement.terr(i) = generalObjectiveFunction([path_shank filesep files_shank(shank_measurement_order(i)).name],0,0,1,'relative',shank_channel);
    shank.measurement.all(i) = generalObjectiveFunction([path_shank filesep files_shank(shank_measurement_order(i)).name],1,1,1,'relative',shank_channel);

    shank.position.total(i) = generalObjectiveFunction([path_shank filesep files_shank(shank_position_order(i)).name],1,0,0,'relative',shank_channel);
    shank.position.peak(i) = generalObjectiveFunction([path_shank filesep files_shank(shank_position_order(i)).name],0,1,0,'relative',shank_channel);
    shank.position.terr(i) = generalObjectiveFunction([path_shank filesep files_shank(shank_position_order(i)).name],0,0,1,'relative',shank_channel);
    shank.position.all(i) = generalObjectiveFunction([path_shank filesep files_shank(shank_position_order(i)).name],1,1,1,'relative',shank_channel);
end

