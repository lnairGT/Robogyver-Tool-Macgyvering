% Normalizing the point cloud positioning

function [point_cloud] = pcl_tf(point_cloud)

xyz0 = mean(point_cloud.Location);
A = bsxfun(@minus, point_cloud.Location, xyz0);

[~,~,V] = svd(A,0);
A_rot = A*V;

A_final = bsxfun(@minus, A_rot, [min(A_rot(:,1)) 0 0]);

point_cloud = pointCloud(A_final);

end