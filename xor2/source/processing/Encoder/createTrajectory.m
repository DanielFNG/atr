function trajectory = createTrajectory(average_slices, cycles)
% Given gait cycle slices, repeat these a given number of times to obtain a
% trajectory i.e. a repition of these average movements.

avg_size = size(average_slices,1);
n = avg_size * cycles;
trajectory = zeros(n,2,3);
count = 1;

for i=1:n
    trajectory(i,1,1) = average_slices(count,1,1);
    trajectory(i,1,2) = average_slices(count,1,2);
    trajectory(i,1,3) = average_slices(count,1,3);
    trajectory(i,2,1) = average_slices(count,2,1);
    trajectory(i,2,2) = average_slices(count,2,2);
    trajectory(i,2,3) = average_slices(count,2,3);
    count = count + 1;
    if count > avg_size
        count = count - avg_size;
    end
end

end

