% Directory.
dir = 'C:\Users\Daniel\Documents\GitHub\atr\xor2\source\optimisation\Data\BruteForceFullSearch';
model = 'C:\Users\Daniel\Documents\GitHub\atr\xor2\source\optimisation\ReferenceData\XoR2-correct-bushing-locations-new-default-coords.osim';

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
results = zeros(length(thigh_points), length(shank_points));

% Loop over the grid and poll the value of cmcObjective. 
for thigh=thigh_points
    for shank=shank_points
        results_folder = [dir filesep 'thigh=' num2str(thigh) 'shank=' num2str(shank) filesep 'CMC'];
        try
            result = CMCResults([results_folder filesep 'XoR2-Human'], 1); % 1 is an ugly way of saying no moment arms
            hamstringPower = ...
            calculateAvgUniMusclePower(result, 'semimem_r', total_mass) + ...
            calculateAvgUniMusclePower(result, 'semiten_r', total_mass) + ...
            calculateAvgUniMusclePower(result, 'bifemlh_r', total_mass) + ...
            calculateAvgUniMusclePower(result, 'bifemsh_r', total_mass);
        catch
            hamstringPower = 50;
        end
        results(thigh/step_size + thigh_offset, ...
            shank/step_size + shank_offset) = hamstringPower;
    end
end

