function result = objectiveFunction(waveforms)
% Objective function for use in the optimisation. 

result = 0;
n_waveforms = size(waveforms,2);
for i=1:n_waveforms
    result = result + mean(waveforms{1,i});
end
result = result/n_waveforms;

end

