n_iterations = 30;

thigh = optimizableVariable('thigh', [0.0, 10.0]);

fun = @evaluateThigh;

results = bayesopt(fun, thigh, ...
    'AcquisitionFunctionName', 'expected-improvement', ...
    'MaxObjectiveEvaluations', n_iterations, ...
    'OutputFcn', @saveToFile, ...
    'SaveFileName', 'ThighEI');