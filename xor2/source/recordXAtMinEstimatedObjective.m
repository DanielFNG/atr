function stop = recordXAtMinEstimatedObjective(results, state)

    global XTrace;

    stop = false;
    if ~strcmp(state, 'done')
        XTrace = [XTrace results.XAtMinEstimatedObjective{1,1}];
    end
    
end

