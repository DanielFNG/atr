% x0 = [0, 0];
% lb = [0, 0.5];
% ub = [10.0, 11.5];
% A = [];
% b = [];
% Aeq = [];
% beq = [];
% fun = @cmcObjective;
% 
% options = psoptimset(@patternsearch);
% options = psoptimset(options,'TolMesh',0.5);
% 
% [x, fval, exitflag, output] = patternsearch(fun, x0, A, b, Aeq, beq, lb, ub);

% Define the step size of the linear grid we search through.
step_size = 0.5;

% Domain of the thigh and shank cuffs.
thigh_points = 6.5:step_size:10.0;
shank_points = 0.5:step_size:11.5;

% For setting the results matrix values correctly. 
thigh_offset = 1 - thigh_points(1)/step_size;
shank_offset = 1 - shank_points(1)/step_size;

% Initialise a results matrix.
results = zeros(length(thigh_points), length(shank_points));

% Loop over the grid and poll the value of cmcObjective. 
for thigh=thigh_points
    for shank=shank_points
        newCMCObjective(thigh, shank);
    end
end
