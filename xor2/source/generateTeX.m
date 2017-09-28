function generateTeX(folder, output, channel, order)
% Function to produce a file with the TeX for results tables. The input 
% argument 'folder' should be a folder in 'xor2/data'. The optional 
% argument 'order' determines the order in which the files should be read.
% Channel is also optional, see generalObjectiveFunction for usage. 

% Get the path to the folder. 
path = [getenv('XOR2') filesep 'data' filesep folder];

% List the files in the folder. 
files = dir(path);

% 
if nargin == 2
    if strcmp(folder,'span')
        order = [6,11,19,5,15,20,16,18,8,9,14,10,23,13,12,17,21,4,7,22,3];
        channel = [4];
    elseif strcmp(folder,'shank_span')
        order = [3,7,8,13,4,14,10,11,5,9,15,12];
        channel = [1];
    else
        % Start from 3 to ignore '.' and '..' filenames.
        order = 3:size(files,1);
    end
end

% Open a file to write the TeX.
fileID = fopen(output, 'w');
formatSpec = ['$%i$ & $%2.1f$ & $%2.2f$ & $%2.2f$ & $%2.2f$ & $%2.2f$' ...
    '& $%2.2f$ & $%2.2f$ & $%2.2f$ & $%2.2f$ \\\\ \n'];

for i=1:size(order,2)
    fprintf(fileID, formatSpec, i, str2double(files(order(i)).name(1:size(files(order(i)).name,2)-6))+str2double(files(order(i)).name(end-4))/10, ...
        generalObjectiveFunction([path filesep files(order(i)).name],1,0,0,'absolute',channel), ...
        generalObjectiveFunction([path filesep files(order(i)).name],0,1,0,'absolute',channel), ...
        generalObjectiveFunction([path filesep files(order(i)).name],0,0,1,'absolute',channel), ...
        generalObjectiveFunction([path filesep files(order(i)).name],1,1,1,'absolute',channel), ...
        generalObjectiveFunction([path filesep files(order(i)).name],1,0,0,'relative',channel), ...
        generalObjectiveFunction([path filesep files(order(i)).name],0,1,0,'relative',channel), ...
        generalObjectiveFunction([path filesep files(order(i)).name],0,0,1,'relative',channel), ...
        generalObjectiveFunction([path filesep files(order(i)).name],1,1,1,'relative',channel));
end

fclose(fileID);

end
