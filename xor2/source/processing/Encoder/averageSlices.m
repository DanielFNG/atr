function averaged_slices = averageSlices(left, right, locs)
% Given the left/right encoder data from the XoR2, as well as a 2D array of
% locations where the first column is for right and second left (such as is
% returned from the identifyGaitCycle script), take slices from the data
% according to these locations for each co-ordinate and average the resulting 
% slices.
%
% The length of the average result (x) (i.e. frames) is the average of the
% frames of the identified slices, rounded to the nearest integer. 
%
% Returns a x by 2 by 3 array, which is the averaged slices. 
%
% This function is used to form the reference gait trajectories from
% measured data for the XoR2.

% How many cycles are we aiming for per co-ordinate.
n_cycles = size(locs,1)-1;

% Find the length to use for the average slice. Also calculate the left and
% right lengths independently, as a working assumption is that the
% difference between these values will be minimal.
length = 0;
right_length = 0;
left_length = 0;
for i=1:n_cycles
    right_length = right_length + locs(i+1,1) - locs(i,1);
    left_length = left_length + locs(i+1,2) - locs(i,2);
    
    length = length + locs(i+1,1) - locs(i,1) + locs(i+1,2) - locs(i,2);
end
right_length = round(right_length/n_cycles,0);
left_length = round(left_length/n_cycles,0);
length = round(length/(2*n_cycles),0); 

% Throw an error if the discrepancy between left/right is too large.
if right_length > 1.1*left_length || right_length < 0.9*left_length
    error('Discrepancy between left and right lengths is too large.')
end

% Create a cell array to hold the different slices of data. 
slices{n_cycles,2,3} = {};

% Isolate each slice and store it in slices.
% The ordering below is according to how the motor encoders are wired for
% the exoskeleton. 
for i=1:size(locs,1)-1
    slices{i,1,1} = right(locs(i,1):locs(i+1,1),2);
    slices{i,1,2} = right(locs(i,1):locs(i+1,1),1);
    slices{i,1,3} = right(locs(i,1):locs(i+1,1),4);
    slices{i,2,1} = left(locs(i,2):locs(i+1,2),1);
    slices{i,2,2} = left(locs(i,2):locs(i+1,2),2);
    slices{i,2,3} = left(locs(i,2):locs(i+1,2),4); 
end

% Stretch or compress each slice to be of the average size.
for i=1:n_cycles
    for j=1:3
        slices{i,1,j} = stretchVector(slices{i,1,j}, length);
        slices{i,2,j} = stretchVector(slices{i,2,j}, length);
    end
end

% Average over the slices for each co-ordinate. 
averaged_slices = zeros(length,2,3);
half_length = round(length/2,0);
for i=1:3
    for j=1:length
        total = zeros(2,1);
        for k=1:n_cycles
            total(1,1) = total(1,1) + slices{k,1,i}(j);
            total(2,1) = total(2,1) + slices{k,2,i}(j);
        end
        averaged_slices(j,1,i) = total(1,1)/n_cycles;
        % Adjust the left averaged slices to account for the phase
        % difference between the left and right leg. 
        if j + half_length <= length
            averaged_slices(j+half_length,2,i) = total(2,1)/n_cycles;
        else
            averaged_slices(j-half_length,2,i) = total(2,1)/n_cycles;
        end
    end
end

end

