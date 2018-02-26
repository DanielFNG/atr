n_iterations = 30;

thigh = optimizableVariable('thigh', [0.0, 10.0]);
shank = optimizableVariable('shank', [0.5, 11.5]);

fun = @matlabCMCObjective;

results = bayesopt(fun, [thigh, shank], 'AcquisitionFunctionName', 'lower-confidence-bound', 'MaxObjectiveEvaluations', n_iterations);