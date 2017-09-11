function order = randomSample(from, by, to)

% Function to randomly sample from an evenly spaced array, specified and 
% constructed via the input arguments i.e. array = from:by:two. 

% Generate all positions. 
x = from:by:to;

% Create the array to store the order.
order = zeros(size(x));

% Shuffle the random seed.
rng('shuffle');

% Set the upper limit for the random number generator.
max = vectorSize(x);

for i=1:max
    % Randomly sample from 1:max+1-i (since each time we loop, we delete a
    % sample).
    y = randi(max+1-i);
    
    % Save in the order array.
    order(i) = x(y);
    
    % Prompt user to sample and say when they're ready for a new point.
    fprintf('\nPlease sample from the point %3.1f.\n', x(y));
    
    if i < max
        while true
            fprintf('Press n for new sample: ');
            str = input('','s');
            if strcmp(str, 'n')
                break;
            end
        end
    end
    
    % Delete the entry that has been sampled. 
    x(y) = [];
end

% Print finished message.
fprintf('Finished sampling.\n');

end

