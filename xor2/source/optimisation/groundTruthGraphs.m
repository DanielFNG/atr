%% Script to create the ground truth graphs. 

thigh_domain = 0:0.5:10.0;
shank_domain = 0.5:1.0:11.5;

% Get fits to the thigh data. 
graph_thigh_total = fit((thigh_domain).',thigh.position.total.','poly7');
graph_thigh_peak = fit((thigh_domain).',thigh.position.peak.','poly7');
graph_thigh_terr = fit((thigh_domain).',thigh.position.terr.','poly7');

% Plot thigh data in a single figure.
figure
subplot(1,3,1)
plot(graph_thigh_total, (thigh_domain).', thigh.position.total.')
subplot(1,3,2)
plot(graph_thigh_peak, (thigh_domain).', thigh.position.peak.')
subplot(1,3,3)
plot(graph_thigh_terr, (thigh_domain).', thigh.position.terr.')

% Get fits to the shank data. 
graph_shank_total = fit((shank_domain).',shank.position.total.','poly7');
graph_shank_peak = fit((shank_domain).',shank.position.peak.','poly7');
graph_shank_terr = fit((shank_domain).',shank.position.terr.','poly7');

% Plot shank data in a single figure. 
figure
subplot(1,3,1)
plot(graph_shank_total, (shank_domain).', shank.position.total.')
subplot(1,3,2)
plot(graph_shank_peak, (shank_domain).', shank.position.peak.')
subplot(1,3,3)
plot(graph_shank_terr, (shank_domain).', shank.position.terr.')