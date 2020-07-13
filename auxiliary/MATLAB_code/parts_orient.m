% Given action, grasp part point clouds, transform their relative
% positioning to match that of the source tool
% Also applies the transformations to the attachment point locations

function [action_pcl_tf, grasp_pcl_tf, min_grasp_x, max_action_x, att_point_action, att_point_grasp] = parts_orient(action_match, grasp_match, angle_relative, pos_relative, part_location, pca_seg)

    action_object = pcread(fullfile(part_location, action_match));
    grasp_object = pcread(fullfile(part_location, grasp_match));
    
    action_object = pcl_tf(action_object);
    action_points = action_object.Location;
    %action_points = action_points*pca_seg;
    action_object = pointCloud(action_points);
    
    grasp_object = pcl_tf(grasp_object);
    
    %figure;
    %pcshowpair(action_object, grasp_object);
    %title('TEST');
    
    att_point_action = att_point_tfm(action_match, action_object);
    att_point_grasp = att_point_tfm(grasp_match, grasp_object);
    
    att_point_action = [att_point_action 1]';
    att_point_grasp = [att_point_grasp 1]';
    
    tform_action = makehgtform('translate', -mean(action_object.Location));
    
    att_point_action = tform_action*att_point_action;
    
    tform_action = affine3d(tform_action');
    action_object = pctransform(action_object, tform_action);

    tform_grasp = makehgtform('translate', -mean(grasp_object.Location)+abs(pos_relative));
    
    att_point_grasp = tform_grasp*att_point_grasp;
    
    tform_grasp = affine3d(tform_grasp');
    grasp_object = pctransform(grasp_object, tform_grasp);
    
    tform_grasp = makehgtform('xrotate', angle_relative(1), ...
         'yrotate', angle_relative(2), 'zrotate', angle_relative(3));
     
    att_point_grasp = tform_grasp*att_point_grasp; 
     
    tform_grasp = affine3d(tform_grasp');
    grasp_object = pctransform(grasp_object, tform_grasp);
    
    max_action_pt = max(action_object.Location);
    max_action_x = max_action_pt(1);
    
    min_grasp_pt = min(grasp_object.Location);
    min_grasp_x = min_grasp_pt(1);
    
    if min_grasp_x > max_action_x
        diff = min_grasp_x - max_action_x; % Towards origin - max_action_x and min_grasp_x is the att_point
    elseif min_grasp_x < max_action_x
        diff = max_action_x - min_grasp_x; % Away from origin - min_action_x
    end

    tform_grasp = makehgtform('translate', [abs(diff),0,0]);
    
    att_point_grasp = tform_grasp*att_point_grasp;
    
    tform_grasp = affine3d(tform_grasp');
    grasp_object = pctransform(grasp_object, tform_grasp);
    
    action_pcl_tf = action_object;
    grasp_pcl_tf = grasp_object;
    
    action_mean_loc = mean(action_object.Location);
    
    max_action_pt = max(action_object.Location);
    max_action_x = [max_action_pt(1), action_mean_loc(2), action_mean_loc(3)];
    
    grasp_mean_loc = mean(grasp_object.Location);
    
    min_grasp_pt = min(grasp_object.Location);
    min_grasp_x = [min_grasp_pt(1), grasp_mean_loc(2), grasp_mean_loc(3)];
    
    att_point_action = att_point_action(1:3);
    att_point_grasp = att_point_grasp(1:3);
    att_point_action = att_point_action';
    att_point_grasp = att_point_grasp';
    
end