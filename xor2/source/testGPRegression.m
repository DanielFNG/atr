% This is a script for testing the GP regression fit to the XoR2 data. 

% Set up the thigh data. 
emg = [7.33, 3.66, -9.35, -9.38, 2.54, -14.14, -17.77, -19.77, -28.50, ...
    -24.82, -5.33, 5.50, -8.94, -7.60, 11.23, 6.69, -1.67, 3.23, -4.98, ...
    0.89, 6.61]';
locs = [1.5, 3.5, 7.5, 1.0, 5.5, 8.0, 6.0, 7.0, 2.0, 2.5, 5.0, 3.0, ...
    9.5, 4.5, 4.0, 6.5, 8.5, 0.5, 10.0, 9.0, 0.0]';
T = sortrows(table(locs, emg));

% Fit the GP's.
rng default
gpfit_septic = fitrgp(T, 'emg', 'BasisFunction', @septicBasis, 'Beta', 1, 'KernelFunction', 'squaredexponential');

% Plot the data. 
figure;
plot(T.locs, T.emg, 'b+', 'DisplayName', 'Data');
hold on;

% Create test space.
xtest = linspace(0,10,1000)';

% Get posterior (?)
[pred, ~, ci] = predict(gpfit_septic, xtest);

% Create posterior/confidence interval plot.
plot(xtest, pred, 'r', 'DisplayName', 'Prediction');
hold on;
plot(xtest, ci(:,1), 'c', 'DisplayName', 'Lower 95% Limit');
plot(xtest, ci(:,2), 'k', 'DisplayName', 'Upper 95% Limit');
legend('show','Location','Best');
shg;

