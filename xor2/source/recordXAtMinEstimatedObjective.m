function stop = recordXAtMinEstimatedObjective(results, state)

    global XTrace;
    global ObservedXTrace;

    stop = false;
    if ~strcmp(state, 'done') && ~strcmp(state, 'initial')
        XTrace = [XTrace results.XAtMinEstimatedObjective{1,1}];
        ObservedXTrace = [ObservedXTrace results.XAtMinObjective{1,1}];
    end
    
end

