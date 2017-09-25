function result = objectiveFunction(waveforms)

result = 0;
n_waveforms = size(waveforms,2);
for i=1:n_waveforms
    result = result + sum(waveforms{1,i});
end

end

