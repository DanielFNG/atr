function loc = bestLocs(locs, A)
    % From a set of locations (i, j)_k stored in a cell matrix locs of 
    % size (1,k) find which gives the minimum value of the matrix A, and 
    % return this location. 

    k = size(locs,2);
    vals = zeros(1,k);
    
    for i=1:size(locs,2)
        vals(i) = A(locs{i}(1,1), locs{i}(1,2));
    end
    
    [~, minloc] = min(vals);
    loc = locs{minloc};
        
end

