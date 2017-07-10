figure(figtraj)
clear('raw_counter1')
load('test_pid.mat')
traj = convertRefTraj(raw_counter1(1:end,1))
hold on
plot(traj)

figure(figerr)
hold on
plot(traj - stationary_ref_traj)