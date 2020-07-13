function point_cloud_new = pi_rot(point_cloud)
    
%Rotate about the Y axis by 180 degrees
A = [cos(pi), 0, sin(pi), 0;... 
     0, 1, 0, 0;...
     -sin(pi), 0, cos(pi), 0;...
     0, 0, 0, 1];
    
tform = affine3d(A);
point_cloud = pctransform(point_cloud, tform);
    
mean_new = mean(point_cloud.Location);
% Translate to original mean
A_final = bsxfun(@minus, point_cloud.Location, [0, mean_new(2), 0]);
point_cloud_new = pointCloud(A_final);
    
end