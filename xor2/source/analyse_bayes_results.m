% Script to analyse the bayes_opt results from the XoR2 stuff. 

% We will calculate the mean and standard deviation of the performance of
% each Bayesian Optimisation method. For the 'plus' acquisition function,
% we will do this as a function of the exploration ratio. For each method,
% we will calculate the performance after 5, 10 and 15 iterations, and plot
% these on the same graph. Our measure of performance will be as follows:
% difference as a percentage between the ACTUAL objective value at the
% PREDICTED optimal point and the ACTUAL objective value at the ACTUAL
% optimal point.

% Store the actual objective values of the thigh and shank curves at the
% actual optimal point. 
load('thigh_fit.mat');
mean = predict(gpfit_sextic, linspace(0, 10, 1000)');
thigh_optimum = max(mean);
load('shank_fit.mat');
mean = predict(shank_gpfit_sextic, linspace(0.5, 11.5, 1000)');
shank_optimum = max(mean);

% First of all, separate the thigh and shank results. 
