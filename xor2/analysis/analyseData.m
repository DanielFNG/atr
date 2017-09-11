function files = analyseData(folder_or_file)
% Produce plots analysing data.
%   If a filename is given as argument, loads file and constructs a bar graph 
%   comparing the unassisted data vs. the assisted data. If a folder is given, 
%   does the same process for each file in the folder, resulting in a bar 
%   plot with twice as many bars as files, where the assistance bars are 
%   plotted over the non-assistance bars. Both files and folders are assumed to 
%   reside in data/.

% Construct path to file/folder.
data_source = [getenv('XOR2') filesep 'data' filesep folder_or_file];

% Construct a cell array to store each of the files to be included. 
if isdir(data_source)
    temp = dir(data_source);
    n_files = vectorSize(temp) - 2;
    files = cell(n_files,1);
    for i=1:n_files
        files{i,1} = temp(i+2).name;
    end
else
    files{1} = data_source;
    
    % Handle the case of a single file within this branch.
end

% Handle the case of a folder. 

    
end

