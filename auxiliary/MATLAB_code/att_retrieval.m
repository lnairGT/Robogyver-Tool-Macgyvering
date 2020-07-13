% Function that takes in action, grasp matches, file names and num_att from
% csv, and returns the attachment points list
% Note that, the grasp location is appended to the original point cloud
% (from the end)

function [att_point_action_list] = att_retrieval(action_match, action_pcl_tf, names, num_att)
    
    [~, action_idx] = ismember(action_match, names);
    %[~, grasp_idx] = ismember(grasp_match, names);
    
    num_att_action = 0;
    %num_att_grasp = 0;
    
    if action_idx ~= 0 %&& grasp_idx ~= 0
        num_att_action = double(num_att(action_idx(1)));
        %num_att_grasp = double(num_att(grasp_idx(1)));
    end
    
    action_points = action_pcl_tf.Location;
    %grasp_points = grasp_pcl_tf.Location;
    
    %num_att_action
    %num_att_grasp
    %ddd
    
    att_point_action_list = action_points(end-num_att_action+1:end, :);
    %att_point_grasp_list = grasp_points(end-num_att_grasp+1:end, :);
    
end