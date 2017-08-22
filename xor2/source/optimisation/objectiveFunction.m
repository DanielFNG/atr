function result = objectiveFunction(waveforms)

%function result = objectiveFunction(processed_emg)
% Objective function for use in the optimisation. 

result = 0;
n_waveforms = size(waveforms,2);
for i=1:n_waveforms
    result = result + mean(waveforms{1,i});
end
result = result/n_waveforms;

% result = 0;
% n = size(processed_emg,2);
% for i=1:n
%     result = result + sum(processed_emg{1,i});
% end
% 
% end

