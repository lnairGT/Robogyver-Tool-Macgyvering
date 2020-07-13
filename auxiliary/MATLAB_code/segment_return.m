%% Compute segments of a segmented point cloud

% Input: Segmented point cloud  
% Output: Returns array of point locations for each segment

function [segments, num_segments] = segment_return(point_cloud)
    point_locations = point_cloud.Location;
    segment_colors = point_cloud.Color;
    
    unique_segments = unique(segment_colors,'rows'); %Unique colors
    
    num_segments = size(unique_segments,1); %Number of segments
    
    segments = zeros(size(point_locations,1),1);
    
    for i = 1:size(unique_segments,1)
        segment_indices = find(segment_colors(:,1)==unique_segments(i,1) ...
            & segment_colors(:,2)==unique_segments(i,2) & segment_colors(:,3)==unique_segments(i,3));
        segments(segment_indices) = i;
    end
    
    % For single segment cases
    if isempty(segment_colors)
       num_segments = 1;
       segments = segments+1;
    end
    
end

