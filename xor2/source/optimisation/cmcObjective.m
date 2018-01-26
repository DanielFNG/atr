function hamstringPower = cmcObjective(thigh, shank)


%% Create the modified model file. 
% Import OpenSim modelling classes.
import org.opensim.modeling.*

% Some defaults. 
model_path = ...
    'ReferenceData\XoR2-correct-bushing-locations-new-default-coords.osim';
save_dir = ['Data' filesep 'TrialRun' filesep 'thigh=' num2str(thigh) ...
    'shank=' num2str(shank)];
save_name = 'model.osim';

% Convert input to bushing locations.
thigh_location_y = -0.17 - thigh/100;

shank_location_x = 0.09 - (shank/100 + 0.10)*tan(deg2rad(14.5));
shank_location_y = -0.13 - shank/100;

% Read the default model file using xmlread.
xml_model = xmlread(model_path);

% Read in the actual model file using the OpenSim API, get access to
% initialise the model state, and get access to the bodies. 
model = Model(model_path);
state = model.initSystem();
markers = model.getMarkerSet();
bodies = model.getBodySet();
test_marker = markers.get('test_marker');

% Find all the weld joints.
weld_joints = xml_model.getElementsByTagName('WeldJoint');

% Body names we need. 
body_names.human = {'femur_r', 'tibia_r', 'femur_l', 'tibia_l'};
body_names.xor2 = {'XoR2_thigh_r', 'XoR2_shank_r', 'XoR2_thigh_l', ...
    'XoR2_shank_l'};

% Correctly ordered strings to look for for the joints. 
joint_names.human = {'bushing_thigh_r_weld', 'bushing_shank_r_weld', ...
    'bushing_thigh_l_weld', 'bushing_shank_l_weld'};
joint_names.xor2 = {'bushing_XoR2_thigh_r_weld', ...
    'bushing_XoR2_shank_r_weld', 'bushing_XoR2_thigh_l_weld', ...
    'bushing_XoR2_shank_l_weld'};

% Loop through the weld joints setting the new locations, using file 
% structure knowledge, currently XoR2 links only.
saved_b_pos{4} = {};
looking_for = 1;
for i=0:weld_joints.getLength()-1
    if looking_for > 4
        break
    elseif strcmp(weld_joints.item(i).getAttribute('name'), ...
            joint_names.xor2{looking_for})
        % Get the current bushing position. 
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
        
        % Increment what we're looking for.
        looking_for = looking_for + 1;
    end
end

% Do the same again but for the human links. 
looking_for = 1;
for i=0:weld_joints.getLength()-1
    if looking_for > 4
        break
    elseif strcmp(weld_joints.item(i).getAttribute('name'), ...
            joint_names.human{looking_for})
        % Get the current bushing position. 
        b_pos = saved_b_pos{looking_for};
        
        % Convert b_pos to the frame of reference of the appropriate 
        % human link.
        test_marker.changeBody(bodies.get(body_names.xor2{looking_for}));
        test_marker.setOffset(b_pos);
        test_marker.changeBodyPreserveLocation(...
            state, bodies.get(body_names.human{looking_for}));
        b_pos_converted = test_marker.getOffset();
        
        % Convert b_pos_converted to a string and set it.
        b_pos_converted = [num2str(b_pos_converted.get(0)) ' ' ...
            num2str(b_pos_converted.get(1)) ' ' ...
            num2str(b_pos_converted.get(2))];
        weld_joints.item(i).getElementsByTagName(...
            'location_in_parent').item(0).setTextContent(b_pos_converted);
        
        % Increment what we're looking for.
        looking_for = looking_for + 1;
    end
end

% Names of the bodies we need - had to reorder.. 
body_names.human{1} = 'femur_l';
body_names.xor2{1} = 'XoR2_thigh_l';
body_names.human{2} = 'tibia_l';
body_names.xor2{2} = 'XoR2_shank_l';
body_names.human{3} = 'femur_r';
body_names.xor2{3} = 'XoR2_thigh_r';
body_names.human{4} = 'tibia_r';
body_names.xor2{4} = 'XoR2_shank_r';

% Find all the Bushing forces.
bushing_forces = xml_model.getElementsByTagName('BushingForce');

% Correctly ordered strings to look for for the bushings. 
names = {'LeftThighBushing', 'LeftShankBushing', 'RightThighBushing', ...
    'RightShankBushing'};

% Loop through the weld joints setting the new locations, using file 
% structure knowledge. 
looking_for = 1;
for i=0:bushing_forces.getLength()-1
    if looking_for > 4
        break
    elseif strcmp(bushing_forces.item(i).getAttribute('name'), ...
            names{looking_for})
        % Get the current bushing position in the frame of reference of 
        % XoR2. 
        b_pos = str2double(strsplit(string(bushing_forces.item(i). ...
            getElementsByTagName('location_body_1').item(0). ...
            getTextContent())));
        
        % Replace b_pos with the new bushing location. 
        if looking_for == 2 || looking_for == 4
            b_pos(1) = shank_location_x;
            b_pos(2) = shank_location_y;
        elseif looking_for < 5
            b_pos(2) = thigh_location_y;
        end
        
        % Convert b_pos to the frame of reference of the appropriate 
        % human link.
        test_marker.changeBody(bodies.get(body_names.xor2{looking_for}));
        test_marker.setOffset(b_pos);
        test_marker.changeBodyPreserveLocation(...
            state, bodies.get(body_names.human{looking_for}));
        b_pos_converted = test_marker.getOffset();
        
        % Convert b_pos to a string and set it.
        b_pos = [num2str(b_pos(1)) ' ' num2str(b_pos(2)) ' ' ...
            num2str(b_pos(3))];
        bushing_forces.item(i).getElementsByTagName(...
            'location_body_1').item(0).setTextContent(b_pos);
        
        % Convert b_pos_converted to a string and set it.
        b_pos_converted = [num2str(b_pos_converted.get(0)) ' ' ...
            num2str(b_pos_converted.get(1)) ' ' ...
            num2str(b_pos_converted.get(2))];
        bushing_forces.item(i).getElementsByTagName(...
            'location_body_2').item(0).setTextContent(b_pos_converted);
        
        % Increment what we're looking for.
        looking_for = looking_for + 1;
    end
end

% Write the updated model file.
xmlwrite([save_dir filesep save_name], xml_model);

%% Perform CMC for 0.5s. 
results_folder = ['C:\Users\Daniel\Documents\GitHub\atr\xor2\source\optimisation\' save_dir filesep 'CMC'];
cmc = CMCTool('ReferenceData\testCMC_TuningBushings.xml');
cmc.setModelFilename(['C:\Users\Daniel\Documents\GitHub\atr\xor2\source\optimisation\' save_dir filesep save_name]);
cmc.loadModel('ReferenceData\testCMC_TuningBushings.xml');
cmc.updateModelForces(cmc.getModel(), 'ReferenceData\testCMC_TuningBushings.xml');
mkdir(results_folder);
cmc.setResultsDir(results_folder);
success = cmc.run();

if success
    result = Data(['C:\Users\Daniel\Documents\GitHub\atr\xor2\source\optimisation\' save_dir filesep 'CMC' filesep 'XoR2-Human_Actuation_power.sto']);
    powers = result.getDataCorrespondingToLabel('semimem_l') + ...
        result.getDataCorrespondingToLabel('semiten_l') + ...
        result.getDataCorrespondingToLabel('bifemlh_l') + ...
        result.getDataCorrespondingToLabel('bifemsh_l') + ...
        result.getDataCorrespondingToLabel('semimem_r') + ...
        result.getDataCorrespondingToLabel('semiten_r') + ...
        result.getDataCorrespondingToLabel('bifemlh_r') + ...
        result.getDataCorrespondingToLabel('bifemsh_r');
    hamstringPower = sum(powers)/vectorSize(powers); % Average power consumption. 
else
    hamstringPower = 1000;
end

% If positive, hamstrings applied energy to model, if negative, hamstrings
% overall took in energy. 

end
