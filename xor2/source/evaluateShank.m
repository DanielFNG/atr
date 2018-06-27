function value = evaluateShank(input_table)

shank = input_table.shank;

% Load the shank data.
load('shank_fit.mat');

% Get the mean and sdev for the point in question.
[mean, sdev] = predict(shank_gpfit_sextic, shank);

% Sample from the distribution.
value = normrnd(-mean, sdev);

end