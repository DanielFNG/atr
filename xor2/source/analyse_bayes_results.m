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
mean_curve = predict(gpfit_sextic, linspace(0, 10, 1000)');
thigh_optimum = max(mean_curve);
load('shank_fit.mat');
mean_curve = predict(shank_gpfit_sextic, linspace(0.5, 11.5, 1000)');
shank_optimum = max(mean_curve);
optima = [thigh_optimum, shank_optimum];

% Load bayes_opt results.
load('bayes_opt_results.mat');

% First of all, separate the thigh and shank results. 
for i=1:2
    figure;
    values = zeros(1,100);
    means = zeros(2,3,3);
    sdevs = zeros(2,3,3);
    
    % Now, separate the acquisition functions.
    for j=1:3
        
        % Now, find the mean and s.dev of the performance over the full set
        % of iterations, after 5, 10 and 15 steps. 
        for L=5:5:15
            for k=1:100
                switch i
                    case 1
                        values(1,k) = predict(gpfit_sextic, ...
                            result_normal{k, i, j}.XTrace(L));
                    case 2
                        values(1,k) = predict(shank_gpfit_sextic, ...
                            result_normal{k, i, j}.XTrace(L));
                end
            end
            values = 100*abs(values - optima(i))./optima(i);
            means(i, j, round(L/5)) = mean(values);
            sdevs(i, j, round(L/5)) = std(values);
        end
    end
    methods = 1:3;
    data = squeeze(means(i, :, :));
    errors = squeeze(sdevs(i, :, :));
    hBar = bar(methods, data);
    for it = 1:size(data, 1)
        ctr(it,:) = bsxfun(@plus, hBar(1).XData, [hBar(it).XOffset]');
        ydt(it,:) = hBar(it).YData;
    end
    hold on;
    errorbar(ctr, ydt, errors, '.r');
    
    % Separate behaviour/plot for the exploration results. 
    for L=1:15
        for k=1:100
            switch i
                case 1 
                    values(1,k) = predict(gpfit_sextic, ...
                        result_explore{
end
    
        
        
        
