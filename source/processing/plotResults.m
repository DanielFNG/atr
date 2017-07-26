%% Plot the filtered EMG data. 
function plotResults(filtered_emg_bicep, averaged_waveforms, labels)
% Labels should be passed in the order:
%   position passive position active position 2 passive...
% i.e. end-p end-a mid-p mid-a

%% Some setup.

% Defaults.
linewidth = 2;
titlefont = 30;
axesfont = 20;
legendfont = 10;

%% Start plotting. 

% Plot all results on one graph.
figure; 
for i=1:size(labels,2)
    plot(filtered_emg_bicep{i}, 'LineWidth', linewidth);
    hold on;
    if i == 1
        title('All Results','FontSize',titlefont)
        xlabel('Frame Number','FontSize',axesfont)
        ylabel('EMG Signal','FontSize',axesfont)
        set(gca, 'FontSize', axesfont)
    end
end
legend(labels, 'FontSize', legendfont)

%% Commenting out below section.
% Can't really see anything meaningful from the graphs. I'll use the above
% graph to illustrate all the data that was collection, then do the
% averaging and present results that way. But I'll keep this plotting code
% just in case. 

% % Split up in to active vs. passive. 
% figure;
% for i=1:2:size(labels,2)-1
%     plot(filtered_emg_bicep{i}, 'LineWidth', linewidth);
%     hold on;
%     if i == 1
%         title('Passive Results', 'FontSize', titlefont)
%         xlabel('Frame Number','FontSize',axesfont)
%         ylabel('EMG Signal','FontSize',axesfont)
%         set(gca, 'FontSize', axesfont)
%     end
% end
% legend({labels{1}, labels{3}, labels{5}}, 'FontSize', legendfont)
% 
% figure;
% for i=2:2:size(labels,2)
%     plot(filtered_emg_bicep{i}, 'LineWidth', linewidth);
%     hold on;
%     if i == 2
%         title('Active Results', 'FontSize', titlefont)
%         xlabel('Frame Number','FontSize',axesfont)
%         ylabel('EMG Signal','FontSize',axesfont)
%         set(gca, 'FontSize', axesfont)
%     end
% end
% legend({labels{2}, labels{4}, labels{6}}, 'FontSize', legendfont)
% 
% % Split it according to context. 
% for i=1:size(labels,2)
%     if i < 3
%         if i == 1
%             figure;
%         end
%         plot(filtered_emg_bicep{i}, 'LineWidth', linewidth);
%         title('End Results', 'FontSize', titlefont)
%         xlabel('Frame Number','FontSize',axesfont)
%         ylabel('EMG Signal','FontSize',axesfont)
%         set(gca, 'FontSize', axesfont)
%         hold on;
%     elseif i == 3 || i == 4
%         if i == 3
%             legend({labels{i-2}, labels{i-1}}, 'FontSize', legendfont)
%             figure;
%         end
%         plot(filtered_emg_bicep{i}, 'LineWidth', linewidth);
%         title('Mid Results', 'FontSize', titlefont)
%         xlabel('Frame Number','FontSize',axesfont)
%         ylabel('EMG Signal','FontSize',axesfont)
%         set(gca, 'FontSize', axesfont)
%         hold on;
%     else
%         if i == 5
%             legend({labels{i-2}, labels{i-1}}, 'FontSize', legendfont)
%             figure;
%         end
%         plot(filtered_emg_bicep{i}, 'LineWidth', linewidth);
%         title('Base Results', 'FontSize', titlefont)
%         xlabel('Frame Number','FontSize',axesfont)
%         ylabel('EMG Signal','FontSize',axesfont)
%         set(gca, 'FontSize', axesfont)
%         hold on;
%     end
% end
% legend({labels{i-1}, labels{i}}, 'FontSize', legendfont)
% 
% % Plot a comparison of active - passive.
% figure;
% for i=1:2:size(labels,2)-1
%     plot(filtered_emg_bicep{i+1}-filtered_emg_bicep{i}, 'LineWidth', linewidth)
%     hold on
%     if i == 1
%         title('Active - Passive','FontSize',titlefont)
%         xlabel('Frame Number','FontSize',axesfont)
%         ylabel('EMG Signal','FontSize',axesfont)
%         set(gca, 'FontSize', axesfont)
%     end
% end
% legend({'end', 'mid', 'base'}, 'FontSize', legendfont)

%% Keeping plots from here. 

% Plot a comparison of the averaged waveforms.
figure;
for i=1:size(labels,2)
    plot(averaged_waveforms{i}, 'LineWidth', linewidth)
    hold on
    if i == 1
        title('Averaged waveforms', 'FontSize', titlefont)
        xlabel('Frame Number', 'FontSize', axesfont)
        ylabel('EMG Signal', 'FontSize', axesfont)
        set(gca, 'FontSize', axesfont)
    end
end
legend(labels, 'FontSize', legendfont)

% Plot a bar graph of the peak activity.
y = zeros(1,size(labels,2));
for i=1:size(labels,2)
    y(1,i) = max(averaged_waveforms{i});
end
figure;
bar(y);
title('Peak activity', 'FontSize', titlefont)
xlabel('Context', 'FontSize', axesfont)
ylabel('Peak EMG signal', 'FontSize', axesfont)
set(gca, 'FontSize', axesfont)
set(gca,'XTickLabel', labels);

% Plot a bar graph of the total activity (sum the array).
z = zeros(1,size(labels,2));
for i=1:size(labels,2)
    z(1,i) = sum(averaged_waveforms{i});
end
figure;
bar(z);
title('Total activity', 'FontSize', titlefont)
xlabel('Context', 'FontSize', axesfont)
ylabel('Summed EMG signal', 'FontSize', axesfont)
set(gca, 'FontSize', axesfont)
set(gca,'XTickLabel', labels);

% Plot a bar graph of the % reduction in peak activity. (Passive -
% active)/passive*100. 
diff_y = zeros(1,size(labels,2)/2);
for i=1:2:size(labels,2)-1
    diff_y(1,i) = 100*((max(averaged_waveforms{i}) - max(averaged_waveforms{i+1}))/max(averaged_waveforms{i}));
end
for i=
diff_y(4) = [];
diff_y(2) = [];
figure;
bar(diff_y);
title('Reduction in peak activity', 'FontSize', titlefont)
xlabel('Context', 'FontSize', axesfont)
ylabel('Summed EMG signal', 'FontSize', axesfont)
set(gca, 'FontSize', axesfont)
set(gca,'XTickLabel', labels(1:2:end));

% Plot a bar graph of the % reduction in total activity. 
diff_z = zeros(1,size(labels,2)/2);
for i=1:2:size(labels,2)-1
    diff_z(1,i) = 100*((sum(averaged_waveforms{i}) - sum(averaged_waveforms{i+1}))/sum(averaged_waveforms{i}));
end
diff_z(4) = [];
diff_z(2) = [];
figure;
bar(diff_z);
title('Reduction in total activity', 'FontSize', titlefont)
xlabel('Context', 'FontSize', axesfont)
ylabel('Summed EMG signal', 'FontSize', axesfont)
set(gca, 'FontSize', axesfont)
set(gca,'XTickLabel', labels(1:2:end));

end