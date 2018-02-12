% This script creates plots for the means and sdevs for the thigh.

thigh_root = 'F:\Dropbox\PhD\Robio 2018\Data\XoR2Data\span';
shank_root = 'F:\Dropbox\PhD\Robio 2018\Data\XoR2Data\shank_span';

% Correct channels.
thigh_channel = 4;
shank_channel = 1;

thigh_names = {};
count = 1;
for i=0:1:10
    thigh_names{count} = [num2str(i) '-0.mat'];
    thigh_names{count + 1} = [num2str(i) '-5.mat'];
    count = count + 2;
end
thigh_names(end) = [];

shank_names = {};
count = 1;
for i=0:1:11
    shank_names{count} = [num2str(i) '-5.mat'];
    count = count + 1;
end

n_thigh_points = length(thigh_names);
n_shank_points = length(shank_names);

thigh_domain = 0:0.5:10;
thigh_means = zeros(n_thigh_points,2);
thigh_sdevs = zeros(n_thigh_points,2);

for i=1:n_thigh_points
    result = computeMeanAndSdev([thigh_root filesep thigh_names{i}], thigh_channel);
    thigh_means(i,1) = result.unassisted.mean;
    thigh_sdevs(i,1) = result.unassisted.sdev;
    thigh_means(i,2) = result.assisted.mean;
    thigh_sdevs(i,2) = result.assisted.sdev;
end

shank_domain = 0.5:1.0:11.5;
shank_means = zeros(n_shank_points,2);
shank_sdevs = zeros(n_shank_points,2);

for i=1:n_shank_points
    result = computeMeanAndSdev([shank_root filesep shank_names{i}], shank_channel);
    shank_means(i,1) = result.unassisted.mean;
    shank_sdevs(i,1) = result.unassisted.sdev;
    shank_means(i,2) = result.assisted.mean;
    shank_sdevs(i,2) = result.assisted.sdev;
end

figure

for i=1:2
    subplot(2,3,i)
    hold on
    bar(thigh_domain, thigh_means(1:end,i));
    errorbar(thigh_domain, thigh_means(1:end,i), thigh_sdevs(1:end,i))
end

relative = 100*(thigh_means(1:end,1) - thigh_means(1:end,2))./thigh_means(1:end,1);
subplot(2,3,3)
bar(thigh_domain, relative)

p_thigh = fit((thigh_domain).',relative,'poly7');
hold on
plot(thigh_domain, p_thigh(thigh_domain));

for i=4:5
    subplot(2,3,i)
    hold on
    bar(shank_domain, shank_means(1:end,i-3));
    errorbar(shank_domain, shank_means(1:end,i-3), shank_sdevs(1:end,i-3))
end

relative = 100*(shank_means(1:end,1) - shank_means(1:end,2))./shank_means(1:end,1);
subplot(2,3,6)
bar(shank_domain, relative)

p_shank = fit((shank_domain).',relative,'poly7');
hold on
plot(shank_domain, p_shank(shank_domain));
    
    
    
    