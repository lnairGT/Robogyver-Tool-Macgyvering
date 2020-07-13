%Given input tool file, retrieve relative parts orientation for the tool

function [angle_relative, pos_relative, pt_close] = relative_params2(input_full_tool_file, action_part, grasp_part)
    %Action part, grasp part
    input_full_tool = pcread(input_full_tool_file);
    [segments_full, num_segments] = segment_return(input_full_tool);
    
    input_full_tool = pcl_tf(input_full_tool);
    
    segment_x = zeros(num_segments,3);
    segment_y = zeros(num_segments,3);
    segment_z = zeros(num_segments,3);
    
    segment_sizes = zeros(1,num_segments);
    
    segment_organized = [];
    
    for i = 1:num_segments
        pt_location = input_full_tool.Location;
        pt_idx = find(segments_full == i);
        pt_location = pt_location(pt_idx,:);
        [~,~,v] = svd(pt_location);
        
        segment_sizes(i) = length(pt_location);
        
        segment_organized = vertcat(segment_organized, pt_location);
        
        segment_x(i,:) = v(:,1);
        segment_y(i,:) = v(:,2);
        segment_z(i,:) = v(:,3);
    end
    
    %Angle between largest axes
    u = segment_x(1,:);
    v = segment_x(2,:);
    angle_x = atan2d(norm(cross(u,v)),dot(u,v))*(pi/180);
    
    %u = segment_y(1,:);
    %v = segment_y(2,:);
    %angle_y = atan2d(norm(cross(u,v)),dot(u,v))*(pi/180);
    
    %u = segment_z(1,:);
    %v = segment_z(2,:);
    %angle_z = atan2d(norm(cross(u,v)),dot(u,v))*(pi/180);
    
    pos_relative = zeros(1,3);
    % NEED TO SPLIT THIS TO PAIRS OF PARTS FOR > 2 SEGMENTS
    for i = 1:num_segments
        pt_location = input_full_tool.Location;
        pt_idx = find(segments_full == i);
        pt_location = pt_location(pt_idx,:);
        pos = mean(pt_location);
        pos_relative = pos - pos_relative;
    end
    
    dist = inf;
    sample = segment_organized(1:segment_sizes(1),:);
    reference = segment_organized(segment_sizes(1)+1:end,:);
    
    for i = 1:length(sample)
        for j = 1:length(reference)
            d = sum((reference(j,:) - sample(i,:)).^2);
            if d < dist
                dist = d;
                pt_close = reference(j);
            end
        end
    end
    
%     vect = mean(sample) - pt_close; %Vector from center to attachment
%     dist = inf;
%     
%     sample = action_part.Location;
%     reference = grasp_part.Location;
%     
%     for i = 1:length(sample)
%         vect2 = mean(sample) - sample(i);
%         theta = atan2d(norm(cross(vect,vect2)),dot(vect,vect2));
%         if theta <= 20
%             d = sum((mean(sample) - sample(i)).^2);
%             if d < dist
%                 dist = d;
%                 att_pt_action = sample(i);
%             end
%         end
%     end
%     
%     vect = mean(reference) - pt_close; %Vector from center to attachment
%     dist = inf;
%     
%     for i = 1:length(reference)
%         vect2 = mean(reference) - reference(i);
%         theta = atan2d(norm(cross(vect,vect2)),dot(vect,vect2));
%         if theta <= 20
%             d = sum((mean(reference) - reference(i)).^2);
%             if d < dist
%                 dist = d;
%                 att_pt_grasp = reference(i);
%             end
%         end
%     end
    
    angle_relative = angle_x;
    
end