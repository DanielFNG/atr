function configureATR()
% Sets the 'ARE_HOME' environment variable and adds the necessary (i.e.
% source) ATR to the Matlab path.  

% Move to the 'main' atr directory. 
cd('..');

% Modify startup.m file so that we have ATR_HOME environment variable
% for future sessions, and the ROBOT_ARM environment variable, and the XOR2
% environment variable. 

% Checks if startup.m file exists, if not one is created in matlabroot if we 
% have access to it, or to the 'Setup/startup' folder of this directory 
% otherwise, if yes the existing one is appended to.
if isempty(which('startup.m'))
    [fileID,~] = fopen([matlabroot filesep 'startup.m'], 'w');
    if fileID == -1
        display(['Attempted to create startup.m file in matlabroot, but' ...
            ' access was denied. Created it in setup\startup folder instead.' ...
            ' Consider changing this as having the startup.m file tied' ...
            ' to a repository can be undesirable.']);
        mkdir(['setup' filesep 'startup']);
        [fileID,~] = fopen(['Setup' filesep 'startup' filesep 'startup.m'], 'w');
        flag = 1;
    else
        flag = 0;
    end
    fprintf(fileID, '%s', ['setenv(''ATR_HOME'', ''' pwd ''');']);
    fprintf(fileID, '%s', ['setenv(''ROBOT_ARM'', ''' [pwd filesep 'robot-arm'] ''');']);
    fprintf(fileID, '%s', ['setenv(''XOR2'', ''' [pwd filesep 'xor2'] ''');']);
else
    fileID = fopen(which('startup.m'), 'a');
    fprintf(fileID, '\n%s', ['setenv(''ATR_HOME'', ''' pwd ''');']);
    fprintf(fileID, '%s', ['setenv(''ROBOT_ARM'', ''' [pwd filesep 'robot-arm'] ''');']);
    fprintf(fileID, '%s', ['setenv(''XOR2'', ''' [pwd filesep 'xor2'] ''');']);
    flag = -1;
end
fclose(fileID);

% Set the environment variable for the current session (necessary so users
% don't have to restart Matlab).
setenv('ATR_HOME', pwd);
setenv('ROBOT_ARM', [pwd filesep 'robot-arm']);
setenv('XOR2', [pwd filesep 'xor2']);

% Modify the Matlab path to include the source folders and the setup folder
% (so it has access to the startup file if it's here).
addpath(genpath([getenv('ROBOT_ARM') filesep 'source']));
addpath(genpath([getenv('ROBOT_ARM') filesep 'offline' filesep 'source']));
addpath(genpath([getenv('ROBOT_ARM') filesep 'online' filesep 'source']));
if flag == 1  
    addpath(genpath([getenv('ATR_HOME') filesep 'setup' filesep 'startup']));
elseif flag == 0
    addpath(matlabroot);
end
savepath;

% Go back to the setup folder. 
cd('setup');

end

