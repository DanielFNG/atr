%% Script to create the ground truth graphs. 

% Get fits to the thigh data. 
graph_thigh_total = fit((1:21).',thigh.position.total.','poly7');
graph_thigh_peak = fit((1:21).',thigh.position.peak.','poly7');
graph_thigh_terr = fit((1:21).',thigh.position.terr.','poly7');

% Plot thigh data in a single figure.
% figure
% subplot(1,3,1)
% plot(graph_thigh_total, (1:21).', thigh.position.total.')
% subplot(1,3,2)
% plot(graph_thigh_peak, (1:21).', thigh.position.peak.')
% subplot(1,3,3)
% plot(graph_thigh_terr, (1:21).', thigh.position.terr.')

% Get fits to the shank data. 
graph_shank_total = fit((1:12).',shank.position.total.','poly7');
graph_shank_peak = fit((1:12).',shank.position.peak.','poly7');
graph_shank_terr = fit((1:12).',shank.position.terr.','poly7');

% Plot shank data in a single figure. 
figure
subplot(1,3,1)
plot(graph_shank_total, (1:12).', shank.position.total.')
subplot(1,3,2)
plot(graph_shank_peak, (1:12).', shank.position.peak.')
subplot(1,3,3)
plot(graph_shank_terr, (1:12).', shank.position.terr.')