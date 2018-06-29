% Uh oh.
global XTrace;

% Decide number of Bayesian Optimisations to carry out for averaging.
n_optimisations = 100;

% Decide number of iterations to carry out per Bayesian Optimisation.
n_iterations = 20;

% Set of acquisition functions to try.
acquisition_functions = {'expected-improvement', ...
    'lower-confidence-bound', 'probability-of-improvement'};
acquisition_plus = 'expected-improvement-plus';

% Set up objective functions to try.
objective_functions = {@evaluateThigh, @evaluateShank};

% Set up optimisation variables to try. 
thigh = optimizableVariable('thigh', [0.0, 10.0]);
shank = optimizableVariable('shank', [0.5, 11.5]);
optimisation_variables = {thigh, shank};

% Create cell arrays to hold results.
result_normal = cell(n_optimisations, length(optimisation_variables), ...
    length(acquisition_functions));
result_explore = cell(n_optimisations, length(optimisation_variables), ...
    length(acquisition_functions));

% Start performing Bayesian optimisations.
for k=1:n_optimisations
    % Perform over the first acquisition function set. 
    for i=1:length(optimisation_variables)
        for j=1:length(acquisition_functions)
            XTrace = [];
            results = bayesopt(objective_functions{i}, ...
                optimisation_variables{i}, ...
                'AcquisitionFunctionName', acquisition_functions{j}, ...
                'MaxObjectiveEvaluations', n_iterations, ...
                'OutputFcn', @recordXAtMinEstimatedObjective);
            result_normal{k, i, j}.XTrace = XTrace;
            result_normal{k, i, j}.result = results;
            close('all');
        end
    end

%     % Perform using acquisition-plus. 
%     for i=1:length(optimisation_variables)
%         for j=0:0.1:1.0
%             XTrace = [];
%             results = bayesopt(objective_functions{i}, ...
%                 optimisation_variables{i}, ...
%                 'AcquisitionFunctionName', acquisition_plus, ...
%                 'MaxObjectiveEvaluations', n_iterations, ...
%                 'ExplorationRatio', j, ...
%                 'OutputFcn', @recordXAtMinEstimatedObjective);
%             result_explore{k, i, round(10*(j+0.1))}.XTrace = XTrace;
%             result_explore{k, i, round(10*(j+0.1))}.result = results;
%             result_explore{k, i, round(10*(j+0.1))}.exploration = j;
%             close('all');
%         end
%     end
end

save('bayes_opt_results.mat', 'result_normal', 'result_explore');