% Function that takes in the point clouds already translated and checks if
% good attachment points for that configuration exist
% It does so by flipping each part and checking for matches - if no matches
% in any configuration, it returns false
% Else, return true with the correct attachment point IDs and poses

function [ranked_score_new, action_part_idx, grasp_part_idx, action_att_points, grasp_att_points, exp_action, exp_grasp, att_type_arr, geo_score, att_score] = att_finder2(action_scores, grasp_scores, parts_files_list, part_location, input_full_tool_file, action_scale, grasp_scale, ranked_action_params, ranked_grasp_params, method)
    
    % Fit scores for different part combinations
    [ranked_score_new, action_part_idx, grasp_part_idx] = parts_combo(action_scores, grasp_scores, action_scale, grasp_scale, ranked_action_params, ranked_grasp_params);
    exp_action = zeros(1,length(action_part_idx));
    exp_grasp = zeros(1,length(grasp_part_idx));
    
    ranked_mult_att = [];
    ranked_mult_action = [];
    ranked_mult_grasp = [];
    action_dist_arr = [];
    grasp_dist_arr = [];
    final_dist = [];
    
    att_type_arr = {};
    geo_score = [];
    att_score = [];
    
    fprintf("Before attachment point consideration ... \n");
    [temp_score_new, idx] = sort(ranked_score_new);
    temp_action = action_part_idx(idx);
    temp_grasp = grasp_part_idx(idx);
    temp_score_new
    temp_action
    temp_grasp
    
    %e_att = [];
    
    % Read for grasp locations
    fid = fopen('num_att.csv');
    out = textscan(fid, '%s%d', 'delimiter', ',');
    fclose(fid);       
    names = out{1};
    num_att = out{2};
    
    [angle_relative, pos_relative, ~] = relative_params(input_full_tool_file);
    att_dist = 0.1; %0.2; %Distance threshold between attachment point and pcl point
 
    %action_att_points = zeros(1,length(ranked_score_new));
    %grasp_att_points = zeros(1,length(ranked_score_new));
    action_att_points = 0;
    grasp_att_points = 0;
    
    for i = 1:length(action_part_idx)
        % Retrieve the corresponding action and grasp part pcl files
        action_match = parts_files_list(action_part_idx(i),:).name;
        grasp_match = parts_files_list(grasp_part_idx(i),:).name;
        
        % Check attachment type to use based on affordance of acting tool
        if contains(grasp_match, 'pliers') || contains(grasp_match, 'tongs')
            att_type = "grasp";
        elseif contains(grasp_match, 'screwdriver')
            att_type = "pierce";
        else
            att_type = "None";
        end
            
        % Orient them based on the input/source tool
        [action_pcl_tf, grasp_pcl_tf, min_grasp_x, max_action_x, att_point_action_list, att_point_grasp_list] = parts_orient4(action_match, grasp_match, angle_relative, pos_relative, part_location, names, num_att, att_type);
        
%         if contains(action_match, "wood_short_midPoint") && contains(grasp_match, "wood_long_endPoint") 
%             fprintf("Here's the action point list \n");    
%             att_point_action_list
%             att_point_grasp_list
%         elseif contains(action_match, "wood_long_endPoint") && contains(grasp_match, "wood_short_midPoint") 
%             fprintf("Here's the action point list \n");    
%             att_point_action_list
%             att_point_grasp_list
%         end  %Debugging
        
        
         %figure; %- UNCOMMENT!!!!!!
         pcshowpair(action_pcl_tf, grasp_pcl_tf);
         pcfull = pcmerge(action_pcl_tf, grasp_pcl_tf, 1);
         pc_name = action_match + "_JOIN_" + grasp_match;
         pcwrite(pcfull, convertCharsToStrings(part_location) + "\" + "CloudConstr\" + pc_name + ".ply");
         pcwrite(pcfull, "CloudConstr\" + pc_name + ".ply");
         %pcshow(pcfull);
%         if ~isempty(att_point_action_list) && ~isempty(att_point_grasp_list)
%             hold on;
%             scatter3(att_point_action_list(:,1), att_point_action_list(:,2), att_point_action_list(:,3));
%             hold on;
%             scatter3(att_point_grasp_list(:,1), att_point_grasp_list(:,2), att_point_grasp_list(:,3));
%         end
%         %hold on;
%         %scatter3(min_grasp_x(1), min_grasp_x(2), min_grasp_x(3));  
%         xlabel('X');
%         ylabel('Y');
%         zlabel('Z');
        
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
        
        if att_type == "pierce"
            att_point_action_list = max_action_x;
            att_point_grasp_list = max_action_x;
        end
        
        % Check if attachment is magnetic
        if (att_type ~= "pierce" && att_type ~= "grasp") && ~isempty(att_point_action_list) && ~isempty(att_point_grasp_list)
            att_type = "magnetic";
        end
        
        
        % Check if attachment type is valid
        if contains(method, "ICRA")
            if att_type == "pierce" || att_type == "grasp"
                att_point_action_list = [];
                att_point_grasp_list = [];
            end
        end
        
        
        if isempty(att_point_action_list) || isempty(att_point_grasp_list)
            grasp_dist_arr = horzcat(grasp_dist_arr, inf);
            action_dist_arr = horzcat(action_dist_arr, inf); 
            att_type = "None"; % No attachment possibilities exist
        else    
            for pt = 1:size(att_point_action_list,1)
                att_point_action = att_point_action_list(pt,:);
                action_dist = sqrt(sum((att_point_action - min_grasp_x).^2));

                if action_dist > att_dist
                    % If not, flip the object and repeat the check
                    fprintf("Attachment points not found.. flipping action object \n");
                    [action_pcl_tf, att_point_action] = pcl_flip(action_pcl_tf, att_point_action);
                    %max_action_pt = max(action_pcl_tf.Location);
                    %max_action_x = max_action_pt(1); 
                    action_dist_temp = sqrt(sum((att_point_action - max_action_x).^2));
                
                    if action_dist_temp > att_dist
                        % The object does not have suitable attachment points
                        if action_dist_temp < action_dist
                            action_dist = action_dist_temp;
                        end
                        fprintf("Action Object with no attachment points \n");
                    end
                end
            action_dist_arr = horzcat(action_dist_arr, action_dist); 
            end
        
            for pt = 1:size(att_point_grasp_list,1)
                % Get distance of attachment point from the point cloud attachment
                att_point_grasp = att_point_grasp_list(pt,:);
                grasp_dist = sqrt(sum((att_point_grasp - max_action_x).^2));
        
                % Repeat above for the grasp parts as well
                if grasp_dist > att_dist
                    fprintf("Attachment points not found.. flipping grasp object \n");
                    [grasp_pcl_tf, att_point_grasp] = pcl_flip(grasp_pcl_tf, att_point_grasp);
                    %min_grasp_pt = min(grasp_pcl_tf.Location);
                    %min_grasp_x = min_grasp_pt(1);
                    grasp_dist_temp = sqrt(sum((att_point_grasp - min_grasp_x).^2));
                    if grasp_dist_temp > att_dist
                        if grasp_dist_temp < grasp_dist
                            grasp_dist = grasp_dist_temp;
                        end
                        fprintf("Grasp Object with no attachment points \n")
                    end
                end        
                grasp_dist_arr = horzcat(grasp_dist_arr, grasp_dist);
            end
        
            %action_match
            %grasp_match
            %action_dist
            %grasp_dist
        end
        
        for val = 1:length(action_dist_arr)
            for val2 = 1:length(grasp_dist_arr)
                dist = action_dist_arr(val) + grasp_dist_arr(val2);
                
                % Doesn't work correctly.. debug
                %if ~contains(grasp_match, "pliers") && ~contains(grasp_match, "screwdriver")
                %    dist = 1000.0;
                %Check if action part pierceable in case of pierce
                %attachment: Need to get list of pierceable objects
                %elseif att_type == "pierce" && grasp_match in obj_list
                %end
                
                final_dist = horzcat(final_dist, dist);
                att_type_arr = horzcat(att_type_arr, att_type); % Save attachment type
            end
        end
        
        %action_att_points(i) = att_point_action_ID;
        %grasp_att_points(i) = att_point_grasp_ID;
        
        %ranked_score_new(i) = ranked_score_new(i) + 5*(action_dist + grasp_dist); %Based on att points
        ranked_mult_att = horzcat(ranked_mult_att, ranked_score_new(i) + 5*(final_dist));
        ranked_mult_action = horzcat(ranked_mult_action, action_part_idx(i)*ones(1,length(final_dist)));
        ranked_mult_grasp = horzcat(ranked_mult_grasp, grasp_part_idx(i)*ones(1,length(final_dist)));
        
        % For recording output
        geo_score = horzcat(geo_score, ranked_score_new(i) + zeros(1,length(final_dist)));
        att_score = horzcat(att_score, final_dist);
        
        %Re initialize all arrays
        action_dist_arr = [];
        grasp_dist_arr = [];
        final_dist = [];
        
        % If either one of the object pair does not have pierce or
        % object-grasp affordance
        
        %e_att = horzcat(e_att, action_dist + grasp_dist);
  
    end
    
    [ranked_score_new, ranked_idx] = sort(ranked_mult_att); %Sort in ascending order (low score better)
    
    %action_att_points = action_att_points(ranked_idx);
    %grasp_att_points = grasp_att_points(ranked_idx);
    
    action_part_idx = ranked_mult_action(ranked_idx);
    grasp_part_idx = ranked_mult_grasp(ranked_idx);
    
    % ACTION_PART_IDX, GRASP_PART_IDX BASED ON GEOMETRIC SCORE ONLY -
    [geo_score, geo_rank] = sort(geo_score);
    att_score = att_score(geo_rank);
    action_part_idx = ranked_mult_action(geo_rank);
    grasp_part_idx = ranked_mult_grasp(geo_rank);
    
    att_type_arr = att_type_arr(geo_rank);
    
    %exp_action = exp_action(ranked_idx);
    %exp_grasp = exp_grasp(ranked_idx);
    %e_att = var(e_att);
end
