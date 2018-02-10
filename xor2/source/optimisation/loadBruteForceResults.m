% Directory.
dir = 'F:\Dropbox\PhD\Robio 2018\Data\BruteForceFullSearch';
model = 'C:\Users\danie\Documents\GitHub\atr\xor2\source\optimisation\ReferenceData\XoR2-correct-bushing-locations-new-default-coords.osim';

% Calc mass of the model. 
import org.opensim.modeling.Model;
model = Model(model);
bodies = model.getBodySet();
n_bodies = bodies.getSize();
total_mass = 0;
for i=1:n_bodies
    total_mass = total_mass + bodies.get(i-1).getMass();
end

% Define the step size of the linear grid we search through.
step_size = 0.5;

% Domain of the thigh and shank cuffs.
thigh_points = 0:step_size:10.0;
shank_points = 0.5:step_size:11.5;

% For setting the results matrix values correctly. 
thigh_offset = 1 - thigh_points(1)/step_size;
shank_offset = 1 - shank_points(1)/step_size;

% Initialise a results matrix.
results_power = zeros(length(thigh_points), length(shank_points));
results_activation = zeros(length(thigh_points), length(shank_points));
results_total_power = zeros(length(thigh_points), length(shank_points));

% Loop over the grid and poll the value of cmcObjective. 
for thigh=thigh_points
    for shank=shank_points
        results_folder = [dir filesep 'thigh=' num2str(thigh) 'shank=' num2str(shank) filesep 'CMC'];
        try
            result = CMCResults([results_folder filesep 'XoR2-Human'], 1); % 1 is an ugly way of saying no moment arms
%             hamstringPower = ...
%             calculateAvgUniMusclePower(result, 'semimem_r', total_mass) + ...
%             calculateAvgUniMusclePower(result, 'semiten_r', total_mass) + ...
%             calculateAvgUniMusclePower(result, 'bifemlh_r', total_mass) + ...
%             calculateAvgUniMusclePower(result, 'bifemsh_r', total_mass);
            gas_power = calculateAvgUniMusclePower(result, 'med_gas_r', total_mass) + calculateAvgUniMusclePower(result, 'lat_gas_r', total_mass);
            time = result.activations.Timesteps;
            total_gas_power = gas_power*(time(end)-time(1));
            activation = result.activations.getDataCorrespondingToLabel('med_gas_r') + result.activations.getDataCorrespondingToLabel('lat_gas_r');
            gas_activation = ...
                trapz(time, activation)/(total_mass*(time(end)-time(1)));
        catch ME
%             hamstringPower = 50;
            total_gas_power = 50;
            gas_power = 50;
            gas_activation = 50;
        end
        results_power(thigh/step_size + thigh_offset, ...
            shank/step_size + shank_offset) = gas_power;
        results_total_power(thigh/step_size + thigh_offset, ...
            shank/step_size + shank_offset) = total_gas_power;
        results_activation(thigh/step_size + thigh_offset, ...
            shank/step_size + shank_offset) = gas_activation;
    end
end

% Remove the 50's.
results_power(results_power == 50) = 0;
results_total_power(results_total_power == 50) = 0;
results_activation(results_activation == 50) = 0;
max_power = max(max(results_power));
max_total_power = max(max(results_total_power));
max_activation = max(max(results_activation));
results_power(results_power == 0) = max_power;
results_total_power(results_total_power == 0) = max_total_power;
results_activation(results_activation == 0) = max_activation;

% Calculate the reduction at each cuff position as a percentage of the
% maximum. 
percentage_power = (max_power - results_power)/max_power*100;
percentage_total_power = (max_total_power - results_total_power)/max_total_power*100;
percentage_activation = (max_activation - results_activation)/max_activation*100;
