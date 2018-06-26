% This is a script for testing the GP regression fit to the XoR2 data. 

% Set up the thigh data. 
emg = -[7.33, 3.66, -9.35, -9.38, 2.54, -14.14, -17.77, -19.77, -28.50, ...
    -24.82, -5.33, 5.50, -8.94, -7.60, 11.23, 6.69, -1.67, 3.23, -4.98, ...
    0.89, 6.61]';
locs = [1.5, 3.5, 7.5, 1.0, 5.5, 8.0, 6.0, 7.0, 2.0, 2.5, 5.0, 3.0, ...
    9.5, 4.5, 4.0, 6.5, 8.5, 0.5, 10.0, 9.0, 0.0]';
T = sortrows(table(locs, emg));

shank_emg = -[-0.93, -16.0, -10.96, -38.04, 1.01, -6.25, 12.60, -4.59, ...
    -35.24, -17.51, -38.30, 2.07]';
shank_locs = [0.5, 11.5, 2.5, 7.5, 1.5, 8.5, 4.5, 5.5, 10.5, 3.5, 9.5, ...
    6.5]';
shank_T = sortrows(table(shank_locs, shank_emg));


% Fit the GP's.
rng default
gpfit_sextic = fitrgp(T, 'emg', 'BasisFunction', @sexticBasis, 'Beta', 1, 'KernelFunction', 'squaredexponential');
shank_gpfit_sextic = fitrgp(shank_T, 'shank_emg', 'BasisFunction', @sexticBasis, 'Beta', 1, 'KernelFunction', 'squaredexponential');

% Save the GP fits for future use.
save('thigh_fit.mat', 'gpfit_septic');
save('shank_fit.mat', 'shank_gpfit_sextic');

% Plot the thigh data. 
figure;

% Create test space.
xtest = linspace(0,10,1000)'; % Sample space to 3 decimal places.

% Get posterior (?)
[pred, ~, ci] = predict(gpfit_sextic, xtest);

% Create posterior/confidence interval plot.
xtest_flipped = [xtest; flipud(xtest)];
in_between = [ci(:,1); flipud(ci(:,2))];
fill(xtest_flipped, in_between, [0.8 0.8 0.8], 'DisplayName', '95% prediction interval');
hold on;
plot(T.locs, T.emg, 'r*', 'DisplayName', 'Observations');
plot(xtest, pred, 'b', 'DisplayName', 'GP Prediction');
plot(xtest, ci(:,1), 'k', 'HandleVisibility', 'off');
plot(xtest, ci(:,2), 'k', 'HandleVisibility', 'off');
legend('show','Location','Best');
xlabel('Cuff Location (cm)');
ylabel('% EMG Reduction');
title('Thigh');
shg;

% Plot the shank data.
figure;

% Create test space.
xtest = linspace(0.5, 11.5, 1000)';

% Get posterior (?)
[pred, ~, ci] = predict(shank_gpfit_sextic, xtest);

% Create posterior/confidence interval plot.
xtest_flipped = [xtest; flipud(xtest)];
in_between = [ci(:,1); flipud(ci(:,2))];
fill(xtest_flipped, in_between, [0.8 0.8 0.8], 'DisplayName', '95% prediction interval');
hold on;
plot(shank_T.shank_locs, shank_T.shank_emg, 'r*', 'DisplayName', 'Observations');
plot(xtest, pred, 'b', 'DisplayName', 'GP Prediction');
plot(xtest, ci(:,1), 'k', 'HandleVisibility', 'off');
plot(xtest, ci(:,2), 'k', 'HandleVisibility', 'off');
legend('show','Location','Best');
xlabel('Cuff Location (cm)');
ylabel('% EMG Reduction');
title('Shank');
xlim([0.5 11.5]);
shg;


