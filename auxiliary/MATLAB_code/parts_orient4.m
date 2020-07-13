% Given action, grasp part point clouds, transform their relative
% positioning to match that of the source tool
% Also applies the transformations to the attachment point locations

function [action_pcl_tf, grasp_pcl_tf, min_grasp_x, max_action_x, att_point_action, att_point_grasp] = parts_orient4(action_match, grasp_match, angle_relative, pos_relative, part_location, names, num_att, att_type)

    action_object = pcread(fullfile(part_location, action_match));
    grasp_object = pcread(fullfile(part_location, grasp_match));
    
    action_object = pcl_tf(action_object);
    grasp_object = pcl_tf(grasp_object);
    
    % Attachment points for magnetic parts
    att_point_action = att_point_tfm(action_match, action_object);
    att_point_grasp = att_point_tfm(grasp_match, grasp_object);
    
    if ~isempty(att_point_action) && ~isempty(att_point_grasp)
        action_points = action_object.Location;
        grasp_points = grasp_object.Location;
        % Add attachments to point cloud
        action_object = pointCloud(vertcat(action_points, att_point_action));
        grasp_object = pointCloud(vertcat(grasp_points, att_point_grasp));
    end
    
    %if ~isempty(att_point_action) && ~isempty(att_point_grasp)
    %    att_point_action = [att_point_action 1]';
    %    att_point_grasp = [att_point_grasp 1]';
    %end
    
    % Orient grasp relative to action
    tform_action = makehgtform('xrotate', angle_relative(1), ...
         'yrotate', angle_relative(2), 'zrotate', angle_relative(3));
     
    %if ~isempty(att_point_action) && ~isempty(att_point_grasp)
    %    att_point_grasp = tform_grasp*att_point_grasp; 
    %end
     
    tform_action = affine3d(tform_action');
    action_object = pctransform(action_object, tform_action);
    
    % Translate grasp part based on relative position
    tform_action = makehgtform('translate', -mean(action_object.Location)+abs(pos_relative));
    
    %if ~isempty(att_point_action) && ~isempty(att_point_grasp)
    %    att_point_grasp = tform_grasp*att_point_grasp;
    %end
    
    tform_action = affine3d(tform_action');
    action_object = pctransform(action_object, tform_action);
    
    % Compute min and max locations 
    max_action_pt = max(action_object.Location);
    max_action_x = max_action_pt(1);
    
    min_grasp_pt = min(grasp_object.Location);
    min_grasp_x = min_grasp_pt(1);
    
    diff = max_action_x - min_grasp_x;
    
    %if min_grasp_x > max_action_x
    %    diff = min_grasp_x - max_action_x; % Towards origin - max_action_x and min_grasp_x is the att_point
    %elseif min_grasp_x < max_action_x
    %    diff = max_action_x - min_grasp_x; % Away from origin - min_action_x
    %end
    
    tform_action = makehgtform('translate', [-diff,0,0]);
    
    %if ~isempty(att_point_action) && ~isempty(att_point_grasp)
    %    att_point_grasp = tform_grasp*att_point_grasp;
    %end
    
    tform_action = affine3d(tform_action');
    action_object = pctransform(action_object, tform_action);
    
    action_pcl_tf = action_object;
    grasp_pcl_tf = grasp_object;
    
    action_mean_loc = mean(action_object.Location);
    
    max_action_pt = max(action_object.Location);
    max_action_x = [max_action_pt(1), action_mean_loc(2), action_mean_loc(3)];
    
    grasp_mean_loc = mean(grasp_object.Location);
    
    min_grasp_pt = min(grasp_object.Location);
    min_grasp_x = [min_grasp_pt(1), grasp_mean_loc(2), grasp_mean_loc(3)];
    
    if ~isempty(att_point_action) && ~isempty(att_point_grasp)
        %att_point_action = att_point_action(1:3);
        %att_point_grasp = att_point_grasp(1:3);
        %att_point_action = att_point_action';
        %att_point_grasp = att_point_grasp';

        att_point_action = action_object.Location(end-size(att_point_action,1)+1:end,:);
        att_point_grasp = grasp_object.Location(end-size(att_point_grasp,1)+1:end,:);
    end
    
    % If attachment type is grasp, and not magnetic
    if strcmp(att_type, 'grasp')
        att_point_action = att_retrieval(action_match, action_pcl_tf, names, num_att);
        att_point_grasp = min_grasp_x;
    end

end