%% Level 1 MACGYVERING - WITH ATTACHMENT POINTS
% Create composite objects from individual parts to match a source tool

%TO DO:
% - Using maps, containers for object pose and attachment points relations
% - Incorporate improved fitting code
% - Adapt code for >2 segments
% - Adapt code for >1 attachment points

tic;

ground_truth = [7,4]; % Indices of ground truth construction as action part, then grasp part

% FULL TOOL FILE
%input_full_tool_file = 'hammer_8_3dwh.ply';
input_full_tool_file = 'squeegee_1_3dwh.ply';
%input_full_tool_file = 'spoon_1_3dwh.ply';
%input_full_tool_file = 'spatula_1_3dwh.ply';
%input_full_tool_file = 'screwdriver_mod.ply';
%input_full_tool_file = 'screwdriver.ply'; %Not this one
%input_full_tool_file = 'tablefork_14_3dwh.ply';

% TOOL PARTS - ACTION
%input_tool_action_file = 'hammer_8_3dwh1.ply';
input_tool_action_file = 'squeegee_1_3dwh1.ply';
%input_tool_action_file = 'spoon_1_3dwh2.ply';
%input_tool_action_file = 'spatula_1_3dwh2.ply';
%input_tool_action_file = 'screwdriver_mod2.ply';
%input_tool_action_file = 'tablefork_14_3dwh2_poke.ply';

input_tool_action = pcread(input_tool_action_file);

% TOOL PARTS - GRASP
%input_tool_grasp_file = 'hammer_8_3dwh2.ply';
input_tool_grasp_file = 'squeegee_1_3dwh2.ply';
%input_tool_grasp_file = 'spoon_1_3dwh1.ply';
%input_tool_grasp_file = 'spatula_1_3dwh1.ply';
%input_tool_grasp_file = 'screwdriver_mod1.ply';
%input_tool_grasp_file = 'tablefork_14_3dwh1_handle.ply';

input_tool_grasp = pcread(input_tool_grasp_file);

% TYPE FOR SQ FOR EACH SEGMENT
SQ_type_action = 0; %Known type of SQ given as input; 3 is paraboloid
SQ_type_grasp = 0;

figure;
%pcshowpair(input_tool_action, input_tool_grasp);
pcshow(input_full_tool_file);
%title('Input tool')

axis off

%% FIT SQ TO EACH SEGMENT

% Normalize orientation of the parts
input_tool_action_temp = pcl_tf(input_tool_action);
input_tool_grasp_temp = pcl_tf(input_tool_grasp);

figure;
pcshowpair(input_tool_action_temp, input_tool_grasp_temp);
title('Normalized parts')
xlabel('X')
ylabel('Y')
zlabel('Z')

if SQ_type_action == 3
    fprintf('Rotating paraboloid action part so it faces upwards.. \n');
    input_tool_action_temp = pi_rot(input_tool_action_temp);
end

if SQ_type_grasp == 3
    fprintf('Rotating paraboloid grasp part so it faces upwards.. \n');
    input_tool_grasp_temp = pi_rot(input_tool_grasp_temp);
end

[action_params, ~, action_part_pcl, action_res] = SQ_fitting_params(input_tool_action_temp, SQ_type_action);
[grasp_params, ~, grasp_part_pcl, grasp_res] = SQ_fitting_params(input_tool_grasp_temp, SQ_type_grasp);

action_scale = (abs(min(action_part_pcl.Location) - max(action_part_pcl.Location)));
grasp_scale = (abs(min(grasp_part_pcl.Location) - max(grasp_part_pcl.Location)));

figure;
pcshowpair(action_part_pcl, input_tool_action_temp);
title('Action Part');
xlabel('X');
ylabel('Y');
zlabel('Z');

figure;
pcshowpair(grasp_part_pcl, input_tool_grasp_temp);
title('Grasp Part');
xlabel('X');
ylabel('Y');
zlabel('Z');

figure;
pcshowpair(action_part_pcl, grasp_part_pcl);
title('SQ parts');
xlabel('X');
ylabel('Y');
zlabel('Z');

%% ACTION, GRASP MATCH FROM AVAILABLE PARTS

part_location = ''; %Location of part point clouds
parts_path = fullfile(part_location,'*.ply');
file_list = dir(parts_path);

action_scores = zeros(1,length(file_list));
grasp_scores = zeros(1,length(file_list));

if SQ_type_action == 2
    ranked_action_params = zeros(length(file_list),12);
else
    ranked_action_params = zeros(length(file_list),11);
end

if SQ_type_grasp == 2
    ranked_grasp_params = zeros(length(file_list),12);
else
    ranked_grasp_params = zeros(length(file_list),11);
end

for i = 1:length(file_list) % Read each segment file
    filename = file_list(i).name;
    fprintf(filename+"\n");
    point_cloud = pcread(fullfile(part_location,filename));
    
    % Normalize orientation of point cloud
    point_cloud = pcl_tf(point_cloud);
    
    % For paraboloid point clouds
    %if string(filename) == "inputCloud5.ply" || string(filename) == "inputCloud6.ply"
    %    fprintf("Rotating the parabola shape to face upwards.. \n");
    %    point_cloud = pi_rot(point_cloud);
    %end
    
    if contains(filename, "bowl") || contains(filename, "cup")
        fprintf("Rotating the parabola shape to face upwards.. \n");
        point_cloud = pi_rot(point_cloud);
    end
    
    [action_SQ_params, ~, SQ_action_subs, residue_action] = SQ_fitting_params(point_cloud, SQ_type_action);    
    score_action = residue_action;
 
    action_part_scale = (abs(min(SQ_action_subs.Location) - max(SQ_action_subs.Location)));
    
    [grasp_SQ_params, ~, SQ_grasp_subs, residue_grasp] = SQ_fitting_params(point_cloud, SQ_type_grasp);    
    score_grasp = residue_grasp;
    
    grasp_part_scale = (abs(min(SQ_grasp_subs.Location) - max(SQ_grasp_subs.Location)));
    
    ranked_action_params(i,:) = action_SQ_params;
    ranked_grasp_params(i,:) = grasp_SQ_params;
    
    ranked_action_params(i,1:3) = action_part_scale;
    ranked_grasp_params(i,1:3) = grasp_part_scale;
    
    %action_scores(i) = score_action;
    %grasp_scores(i) = score_grasp;
    
    %Compare epsilon and tapering parameters
    action_scores(i) = sum(abs(ranked_action_params(i,4:5) - action_params(4:5))) + sum(abs(ranked_action_params(i,end:end-2) - action_params(end:end-2)));
    grasp_scores(i) = sum(abs(ranked_grasp_params(i,4:5) - grasp_params(4:5))) + sum(abs(ranked_grasp_params(i,end:end-2) - grasp_params(end:end-2)));
    
end

%% FIND IF ATTACHMENT POINTS EXIST, RETURN ATT POINT IDS AND FINAL POINT CLOUD

method = "RSS"; %"ICRA" or "RSS"
[ranked_score_new, action_part_idx, grasp_part_idx, action_att_points, grasp_att_points, ~, ~, att_type_arr, geo_score, att_score] = att_finder2(action_scores, grasp_scores, file_list, part_location, input_full_tool_file, action_scale, grasp_scale, ranked_action_params, ranked_grasp_params, method);

%fprintf("After considering attachment points ... \n");
%ranked_score_new

%Changed the following to reflect geometric score based ranking
%action_part_idx
%grasp_part_idx

%att_type_arr
%geo_score
%att_score

% Find the rank of ground truth
for i = 1:length(action_part_idx)
    if action_part_idx(i) == ground_truth(1) && grasp_part_idx(i) == ground_truth(2)
        rank_score = i;
        break;
    end
end

%% Print results

fprintf("The ground truth is ranked at... \n");
rank_score

fprintf("It's score is... \n");
ranked_score_new(rank_score)

fprintf("Total part combination space is ... \n");
length(action_part_idx)

fprintf("Percentage space explored is ... \n");
(rank_score/length(action_part_idx))*100

%% Save the output to a csv file
% [[obj1_name, obj2_name], geometric_score, att_type, att_score]

outfile = fullfile(part_location,'output_rankings.csv');
output = cell(length(action_part_idx),5);

for i = 1:length(action_part_idx)
    output(i,:) = {file_list(action_part_idx(i)).name, file_list(grasp_part_idx(i)).name, att_type_arr(i), geo_score(i), att_score(i)};
end

cell_header = {'action_part', 'grasp_part', 'attachment', 'geo_score', 'att_score'};

fid = fopen(outfile, 'w');
fprintf(fid, '%s,', cell_header{1,1:end-1});
fprintf(fid, '%s\n', cell_header{1,end});

for i = 1:size(output,1)
    fprintf(fid, '%s,', output{i,1:3});
    fprintf(fid, '%d,', output{i,4});
    fprintf(fid, '%d\n', output{i,5});
end
fclose(fid);

time = toc;

time
close all;