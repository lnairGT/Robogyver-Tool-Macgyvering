% Flip point cloud about its mean point

function [flipped_pcl, att_point_flip] = pcl_flip(pcl, att_point)
 
    att_point_flip = [att_point 1]';

    % Move object to origin
    pcl_mean = mean(pcl.Location);
    tform = makehgtform('translate', -pcl_mean);
    
    att_point_flip = tform*att_point_flip;
    
    tform = affine3d(tform');
    pcl_tf = pctransform(pcl, tform);
    
    % Rotate 180 degrees about the Z axis
    tform = makehgtform('zrotate', pi);
    
    att_point_flip = tform*att_point_flip;
    
    tform = affine3d(tform');
    pcl_tf = pctransform(pcl_tf, tform);
    
    % Move back to original mean
    tform = makehgtform('translate', pcl_mean);
    
    att_point_flip = tform*att_point_flip;
    
    tform = affine3d(tform');
    flipped_pcl = pctransform(pcl_tf, tform);
    
    att_point_flip = att_point_flip(1:3);
    att_point_flip = att_point_flip';
    
end