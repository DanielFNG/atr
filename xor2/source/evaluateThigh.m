function value = evaluateThigh(input_table)

thigh = input_table.thigh;

% Load the thigh data.
load('thigh_fit.mat');

% Get the mean and sdev for the point in question.
[mean, sdev] = predict(gpfit_sextic, thigh);

% Sample from the distribution.
value = normrnd(-mean, sdev);

end