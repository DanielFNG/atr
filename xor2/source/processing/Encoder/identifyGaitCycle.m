function [pks, locs] = identifyGaitCycle(left_measured, right_measured, bounds, limits)
% Given the encoder data (angles) from XoR2, 
% and some bounds = [lower_bound, upper_bound], and optionally some 
% limits = [right_limit, left_limit], isolate the 
% gait cycle by splitting at the maxima of the left/right ankle curves.
%
% left_measured, right_measured and bounds are required, limits is optional and 
% if not given defaults defined below are used.
%
% Assumptions are that the left data has clearer maximums and the right
% data has clearer minimums - due to the difference in direction between
% the encoders. Also that we use the ankle joints in each case. 
%
% Returns [pks, locs] which are matrices whose row indexes the exoskeleton
% side. 1 - right, 2 - left. 

% Parse input arguments, setting defaults if necessary. 
if nargin < 3 || nargin > 4
    error('Require 3 or 4 arguments.')
elseif nargin == 3
    right_limit = 0.3;
    left_limit = 0.32;
else
    right_limit = limits(1);
    left_limit = limits(2);
end

% Settings for ankle joints.
right_index = 2;
left_index = 1;

% Isolate the correct slice of the measured data. 
right_slice = right_measured(bounds(1):bounds(2), right_index);
left_slice = left_measured(bounds(1):bounds(2), left_index);

% Find all of the peaks and peak locations. See assumptions for why we do
% -right_slice. 
[right_pks, right_locs] = findpeaks(-right_slice);
[left_pks, left_locs] = findpeaks(left_slice);

% Discard any peaks which aren't above the limits.
n_right_pks = size(right_pks);
n_left_pks = size(left_pks);

for i=n_right_pks:-1:1
    if right_pks(i) < right_limit
        right_pks(i) = [];
        right_locs(i) = [];
    end
end

for i=n_left_pks:-1:1
    if left_pks(i) < left_limit
        left_pks(i) = [];
        left_locs(i) = [];
    end
end

% Which one got less peaks...
total_peaks = min(size(right_pks), size(left_pks));

% Add on the lower bound so we can continue to use the full angle1/0 arrays
% as input.
right_locs(1:total_peaks) = right_locs(1:total_peaks) + bounds(1) - 1;
left_locs(1:total_peaks) = left_locs(1:total_peaks) + bounds(1) - 1;

% Save right pks/locs together with left and return.
pks = [right_pks(1:total_peaks), left_pks(1:total_peaks)];
locs = [right_locs(1:total_peaks), left_locs(1:total_peaks)];
% We won't really use the pks much later, but useful to return them for
% checking purposes.

end


