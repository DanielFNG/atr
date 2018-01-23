function locs = findIndices(A, valA, B, valB, direction)
    % Given matrices A, B with size(A) = size(B), find the 'first' set of 
    % indices (i, j)_k such that A(i,j) <= valA and B(i,j) <= valB for all 
    % k.
    %
    % 'First' is determined by the 'direction' parameter. If direction 
    % is 'column', we iterate over A and B by column, and if direction is 
    % 'row' we iterate by row. 

    % First check that A and B are of the same size.
    if size(A) ~= size(B)
        error('Input matrices must be of same dimension.');
    end

    % Iterate by row by default (see below). If the opposite is specified, 
    % transpose A and B.  
    if strcmp(direction, 'column')
        A = A.';
        B = B.';
    elseif ~strcmp(direction, 'row')
        error('Direction should be specified as row or column.')
    end

    % Keep track of number of found locs and their values. 
    k = 0;
    locs = {};

    % Iterate along row. 
    for i=1:size(A,1)
        for j=1:size(A,2)
            if A(i,j) < valA && B(i,j) < valB
                k = k + 1;
                if strcmp(direction, 'column')
                    locs{k} = [j, i];
                else
                    locs{j} = [i, j];
                end
            end
        end
        if k > 0
            break;
        end
    end

end

