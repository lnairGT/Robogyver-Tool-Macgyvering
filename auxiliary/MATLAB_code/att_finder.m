% Function that takes in the point clouds already translated and checks if
% good attachment points for that configuration exist
% It does so by flipping each part and checking for matches - if no matches
% in any configuration, it returns false
% Else, return true with the correct attachment point IDs and poses

function [ranked_score_new, action_part_idx, grasp_part_idx, action_att_points, grasp_att_points, exp_action, exp_grasp] = att_finder(action_scores, grasp_scores, parts_files_list, part_location, input_full_tool_file, action_scale, grasp_scale, ranked_action_params, ranked_grasp_params)
    
    % Fit scores for different part combinations
    [ranked_score_new, action_part_idx, grasp_part_idx] = parts_combo(action_scores, grasp_scores, action_scale, grasp_scale, ranked_action_params, ranked_grasp_params);
    exp_action = zeros(1,length(action_part_idx));
    exp_grasp = zeros(1,length(grasp_part_idx));
    
    fprintf("Before attachment point consideration ... \n");
    [temp_score_new, idx] = sort(ranked_score_new);
    temp_action = action_part_idx(idx);
    temp_grasp = grasp_part_idx(idx);
    temp_score_new
    temp_action
    temp_grasp
    
    %e_att = [];
    
    [angle_relative, pos_relative, pca_seg] = relative_params(input_full_tool_file);
    att_dist = 0.2; %Distance threshold between attachment point and pcl point
    
    action_att_points = zeros(1:length(ranked_score_new));
    grasp_att_points = zeros(1:length(ranked_score_new));
    
    for i = 1:length(action_part_idx)
        % Retrieve the corresponding action and grasp part pcl files
        action_match = parts_files_list(action_part_idx(i),:).name;
        grasp_match = parts_files_list(grasp_part_idx(i),:).name;
        
        % Orient them based on the input/source tool
        [action_pcl_tf, grasp_pcl_tf, min_grasp_x, max_action_x, att_point_action, att_point_grasp] = parts_orient(action_match, grasp_match, angle_relative, pos_relative, part_location, pca_seg);
        
        [~,~,~,~,s_action] = pca(action_pcl_tf.Location);
        [~,~,~,~,s_grasp] = pca(grasp_pcl_tf.Location);
        
        if s_action(1) > 30
            exp_action(i) = exp_action(i) + 2;
            if s_action(2) > 30
                exp_action(i) = exp_action(i) + 2;
            end
        end
        
        if s_grasp(1) > 30
            exp_grasp(i) = exp_grasp(i) + 2;
            if s_grasp(2) > 30
                exp_grasp(i) = exp_grasp(i) + 2;
            end
        end
        
        % Attachment point IDs for the specified action, grasp parts
        att_point_action_ID = 0; 
        att_point_grasp_ID = 0; 

        figure;
        pcshowpair(action_pcl_tf, grasp_pcl_tf);
        axis off;
        
        % Get distance of attachment point from the point cloud attachment
        action_dist = sqrt(sum((att_point_action - min_grasp_x).^2));
        grasp_dist = sqrt(sum((att_point_grasp - max_action_x).^2));
        
        % Check if attachment points exists within close vicinity on action and grasp parts
        if action_dist > att_dist
            % If not, flip the object and repeat the check
            fprintf("Attachment points not found.. flipping action object \n");
            [action_pcl_tf, att_point_action] = pcl_flip(action_pcl_tf, att_point_action);
            max_action_pt = max(action_pcl_tf.Location);
            max_action_x = max_action_pt(1);
            action_dist_temp = sqrt(sum((att_point_action - max_action_x).^2));
            if action_dist_temp > att_dist
                % The object does not have suitable attachment points
                if action_dist_temp < action_dist
                    action_dist = action_dist_temp;
                end
                fprintf("Action Object with no attachment points \n");
            end
        end
        
        % Repeat above for the grasp parts as well
        if grasp_dist > att_dist
            fprintf("Attachment points not found.. flipping grasp object \n");
            [grasp_pcl_tf, att_point_grasp] = pcl_flip(grasp_pcl_tf, att_point_grasp);
            min_grasp_pt = min(grasp_pcl_tf.Location);
            min_grasp_x = min_grasp_pt(1);
            grasp_dist_temp = sqrt(sum((att_point_grasp - min_grasp_x).^2));
            if grasp_dist_temp > att_dist
                if grasp_dist_temp < grasp_dist
                    grasp_dist = grasp_dist_temp;
                end
                fprintf("Grasp Object with no attachment points \n")
            end
        end

        action_att_points(i) = att_point_action_ID;
        grasp_att_points(i) = att_point_grasp_ID;
        
        ranked_score_new(i) = ranked_score_new(i) + 5*(action_dist + grasp_dist); %Based on att points
        
        %e_att = horzcat(e_att, action_dist + grasp_dist);
    end
    
    [ranked_score_new, ranked_idx] = sort(ranked_score_new); %Sort in ascending order (low score better)
    
    action_att_points = action_att_points(ranked_idx);
    grasp_att_points = grasp_att_points(ranked_idx);
    
    action_part_idx = action_part_idx(ranked_idx); % Sorted action part indices
    grasp_part_idx = grasp_part_idx(ranked_idx); % Corresponding grasp part idx
    
    exp_action = exp_action(ranked_idx);
    exp_grasp = exp_grasp(ranked_idx);
    
    %e_att = var(e_att)
end
