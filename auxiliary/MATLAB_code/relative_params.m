%Given input tool file, retrieve relative parts orientation for the tool

function [angle_relative, pos_relative, pca_seg] = relative_params(input_full_tool_file)
    input_full_tool = pcread(input_full_tool_file);
    [segments_full, num_segments] = segment_return(input_full_tool);
    
    input_full_tool = pcl_tf(input_full_tool);
    
    segment_x = zeros(num_segments,3);
    segment_y = zeros(num_segments,3);
    segment_z = zeros(num_segments,3);
    
    for i = 1:num_segments
        pt_location = input_full_tool.Location;
        pt_idx = find(segments_full == i);
        pt_location = pt_location(pt_idx,:);
        [~,~,v] = svd(pt_location);
        
        segment_x(i,:) = v(:,1);
        segment_y(i,:) = v(:,2);
        segment_z(i,:) = v(:,3);
    end
    
    u = segment_x(1,:);
    v = segment_x(2,:);
    angle_x = atan2d(norm(cross(u,v)),dot(u,v))*(pi/180);
    
    u = segment_y(1,:);
    v = segment_y(2,:);
    angle_y = atan2d(norm(cross(u,v)),dot(u,v))*(pi/180);
    
    u = segment_z(1,:);
    v = segment_z(2,:);
    angle_z = atan2d(norm(cross(u,v)),dot(u,v))*(pi/180);
    
    pos_relative = zeros(1,3);
    % NEED TO SPLIT THIS TO PAIRS OF PARTS FOR > 2 SEGMENTS
    for i = 1:num_segments
        pt_location = input_full_tool.Location;
        pt_idx = find(segments_full == i);
        pt_location = pt_location(pt_idx,:);
        pos = mean(pt_location);
        pos_relative = pos - pos_relative;
    end
    
    pca_seg = [segment_x(1,:)' segment_y(1,:)' segment_z(1,:)'];
    
    angle_relative = [angle_x, angle_y, angle_z];
    
end