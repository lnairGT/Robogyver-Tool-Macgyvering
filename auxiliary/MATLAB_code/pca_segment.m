%% Compute PCA for PCL segments to get segment orientation

%Input - pcl of the segment
%Output - segment projected using pca 

function [new_segments, inv_pca] = pca_segment(pcl)

    segments = pointCloud(pcl);
    
    % Downsample point cloud if necessary to improve fitting speed
    %gridStep = 0.01;
    %segments_temp = pcdownsample(segments, 'gridAverage', gridStep);
    
    %if size(segments_temp, 1) > 1000 % At least 1000 points in downsampled version
    %    segments = segments_temp;
    %end
    
    segments = segments.Location;
    
    pca_segments = pca(segments);
    new_segments = segments*pca_segments;
    inv_pca = inv(pca_segments);

end