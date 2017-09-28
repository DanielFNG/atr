function tracking_error = computeTrackingError(data, reference, peaks)
% Compute the tracking error as a percentage of the reference trajectory.

n_peaks = size(peaks,2);
difference = zeros(n_peaks-1,1);
for i=1:n_peaks-1
    difference(i,1) = 0;
    for j=peaks(i):peaks(i+1)
        difference(i) = difference(i) + abs(data(j,4) - reference(j,1,3));
    end
end
tracking_error = mean(difference);

end

