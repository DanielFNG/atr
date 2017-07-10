clear('raw_counter_1')
load('test2.mat')
figure
plot(reference_trajectory)
hold on
plot(raw_counter1(1:end,1))