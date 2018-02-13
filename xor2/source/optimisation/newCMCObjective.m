function newCMCObjective(thigh, shank)


%% Create the modified model file. 
% Import OpenSim modelling classes.
import org.opensim.modeling.*

if nargin == 1
    if length(thigh) == 2
        shank = thigh(2);
        thigh = thigh(1);
    else
        error('weird input arguments');
    end
elseif nargin ~= 2
    error('weird input arguments');
end
    
% Display info.
fprintf('Searching for thigh %f and shank %f.\n', thigh, shank);

% Some defaults. 
model_path = ...
    'ModelRedraftCopy\XoR2-correct-bushing-locations-new-default-coords.osim';
save_dir = ['F:\Dropbox\PhD\Robio 2018\Data\NewModelBruteForceFullSearch' filesep 'thigh=' num2str(thigh) ...
    'shank=' num2str(shank)];
save_name = 'model.osim';

% Convert input to bushing locations.
thigh_location_y = -0.17 - thigh/100;

shank_location_x = 0.09 - (shank/100 + 0.10)*tan(deg2rad(14.5));
shank_location_y = -0.13 - shank/100;

% Read the default model file using xmlread.
xml_model = xmlread(model_path);

% Find all the weld joints.
weld_joints = xml_model.getElementsByTagName('WeldJoint');

% Correctly ordered strings to look for for the joints. 
joint_names = {'bushing_thigh_r_weld', 'bushing_shank_r_weld', ...
    'bushing_thigh_l_weld', 'bushing_shank_l_weld', ...
    'XoR2_thigh_r_femur_r', 'XoR2_shank_r_tibia_r', ...
    'XoR2_thigh_l_femur_l', 'XoR2_shank_l_tibia_l'};

% Loop through the weld joints setting the new locations, using file 
% structure knowledge, currently XoR2 links only.
n_joints = length(joint_names);
saved_b_pos{n_joints} = {};
looking_for = 1;
for i=0:weld_joints.getLength()-1
    if looking_for > n_joints
        break
    elseif strcmp(weld_joints.item(i).getAttribute('name'), ...
            joint_names{looking_for})
        % Get the current weld position. 
        b_pos = str2double(strsplit(string(weld_joints.item(i). ...
            getElementsByTagName('location_in_parent').item(0). ...
            getTextContent())));
        
        % Replace b_pos with the new bushing location. 
        if mod(looking_for,2) == 0
            b_pos(1) = shank_location_x;
            b_pos(2) = shank_location_y;
        else
            b_pos(2) = thigh_location_y;
        end
        
        % Save the b_pos array. 
        saved_b_pos{looking_for} = b_pos;
        
        % Convert b_pos to a string and set it.
        b_pos = [num2str(b_pos(1)) ' ' num2str(b_pos(2)) ' ' ...
            num2str(b_pos(3))];
        weld_joints.item(i).getElementsByTagName('location_in_parent'). ...
            item(0).setTextContent(b_pos);
        
        % Set location in child to 0.
        c_pos = '0 0 0';
        weld_joints.item(i).getElementsByTagName('location').item(0).setTextContent(c_pos);
        
        % Increment what we're looking for.
        looking_for = looking_for + 1;
    end
end

body_names = {'','','','',...
    'XoR2_thigh_r','XoR2_shank_r','XoR2_thigh_l','XoR2_shank_l'};

% Write the updated model file.
xmlwrite([save_dir filesep save_name], xml_model);
model_path = [save_dir filesep save_name];

% Read in the actual model file using the OpenSim API, get access to
% initialise the model state, and get access to the bodies. 
model = Model(model_path);
state = model.initSystem();
markers = model.getMarkerSet();
bodies = model.getBodySet();
test_marker = markers.get('test_marker');

% Add the location in child frame for the thigh links.
looking_for = 5;
for i=0:weld_joints.getLength()-1
    if looking_for == 5
        body_loc = 'XoR2_link_r';
        body_pos = [0.015 -0.065 0.01015];
    elseif looking_for == 7
        body_loc = 'XoR2_link_l';
        body_pos = [0.015, -0.065 -0.01015];
    elseif looking_for > 8
        break
    end
    
    if strcmp(weld_joints.item(i).getAttribute('name'), ...
        joint_names{looking_for})
        % Change the test marker to the correct location.
        test_marker.changeBody(bodies.get(body_loc));
        test_marker.setOffset(body_pos);
        test_marker.changeBodyPreserveLocation(...
            state, bodies.get(body_names{looking_for}));
        b_vec = test_marker.getOffset();
        b_pos = [-b_vec.get(0), -b_vec.get(1), -b_vec.get(2)];
        
        % Convert b_pos to a string and set it.
        b_pos = [num2str(b_pos(1)) ' ' num2str(b_pos(2)) ' ' ...
            num2str(b_pos(3))];
        weld_joints.item(i).getElementsByTagName(...
            'location').item(0).setTextContent(b_pos);
        
        looking_for = looking_for + 2;
    end
end

% Write the updated model file.
xmlwrite([save_dir filesep save_name], xml_model);
model_path = [save_dir filesep save_name];

% Read in the actual model file using the OpenSim API, get access to
% initialise the model state, and get access to the bodies. 
model = Model(model_path);
state = model.initSystem();
markers = model.getMarkerSet();
bodies = model.getBodySet();
test_marker = markers.get('test_marker');

% Add the location in child frame for the shank links.
looking_for = 6;
for i=0:weld_joints.getLength()-1
    if looking_for == 6
        body_loc = 'XoR2_thigh_r';
        body_pos = [0 -0.38 0.0287];
    elseif looking_for == 8
        body_loc = 'XoR2_thigh_l';
        body_pos = [0 -0.38 -0.028975];
    elseif looking_for > 8
        break
    end
    
    if strcmp(weld_joints.item(i).getAttribute('name'), ...
        joint_names{looking_for})
        % Change the test marker to the correct location.
        test_marker.changeBody(bodies.get(body_loc));
        test_marker.setOffset(body_pos);
        test_marker.changeBodyPreserveLocation(...
            state, bodies.get(body_names{looking_for}));
        b_vec = test_marker.getOffset();
        b_pos = [-b_vec.get(0), -b_vec.get(1), -b_vec.get(2)];
        
        % Convert b_pos to a string and set it.
        b_pos = [num2str(b_pos(1)) ' ' num2str(b_pos(2)) ' ' ...
            num2str(b_pos(3))];
        weld_joints.item(i).getElementsByTagName(...
            'location').item(0).setTextContent(b_pos);
        
        looking_for = looking_for + 2;
    end
end

% Write the updated model file.
xmlwrite([save_dir filesep save_name], xml_model);

%% Perform CMC for 0.5s. 
results_folder = [save_dir filesep 'CMC'];
cmc = CMCTool('ModelRedraftCopy\testCMC_TuningBushings.xml');
cmc.setModelFilename([save_dir filesep save_name]);
cmc.loadModel('ModelRedraftCopy\testCMC_TuningBushings.xml');
cmc.updateModelForces(cmc.getModel(), 'ModelRedraftCopy\testCMC_TuningBushings.xml');
cmc.addAnalysisSetToModel();
mkdir(results_folder);
cmc.setResultsDir(results_folder);
for i=1:3
    success = cmc.run();
    if success
        break
    end
end

% % Calc mass of the model. 
% n_bodies = bodies.getSize();
% total_mass = 0;
% for i=1:n_bodies
%     total_mass = total_mass + bodies.get(i-1).getMass();
% end

% % Try CMC 3 times. 
% for i=1:3
%     success = cmc.run();
%     if success
%         result = CMCResults([results_folder filesep 'XoR2-Human'], 1); % 1 is an ugly way of saying no moment arms
%     %     result = Data(['C:\Users\Daniel\Documents\GitHub\atr\xor2\source\optimisation\' save_dir filesep 'CMC' filesep 'XoR2-Human_Actuation_power.sto']);
%     %     powers = result.getDataCorrespondingToLabel('semimem_l') + ...
%     %         result.getDataCorrespondingToLabel('semiten_l') + ...
%     %         result.getDataCorrespondingToLabel('bifemlh_l') + ...
%     %         result.getDataCorrespondingToLabel('bifemsh_l') + ...
%     %         result.getDataCorrespondingToLabel('semimem_r') + ...
%     %         result.getDataCorrespondingToLabel('semiten_r') + ...
%     %         result.getDataCorrespondingToLabel('bifemlh_r') + ...
%     %         result.getDataCorrespondingToLabel('bifemsh_r');
%     %     hamstringPower = sum(powers)/vectorSize(powers); % Average power consumption.
%         hamstringPower = ...
%             calculateAvgUniMusclePower(result, 'semimem_r', total_mass) + ...
%             calculateAvgUniMusclePower(result, 'semiten_r', total_mass) + ...
%             calculateAvgUniMusclePower(result, 'bifemlh_r', total_mass) + ...
%             calculateAvgUniMusclePower(result, 'bifemsh_r', total_mass);
%         break;
%     end        
%     hamstringPower = 50;
% end

end