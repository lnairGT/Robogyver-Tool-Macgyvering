function [pcl_SQ, SQ_pcl] = pcl_dist(pcl, SQ)

pcl_numpoints = size(pcl,1);
segments = pointCloud(pcl);

%if pcl_numpoints > 1000
%    gridStep = 0.01;
%    segments = pcdownsample(segments, 'gridAverage', gridStep);
%end

% Distance from SQ to pcl
reference = segments.Location;
sample = SQ;

distMat = zeros(size(sample,1),1);
for row_idx = 1:size(sample,1)
    diff = reference-repmat(sample(row_idx,:),size(reference,1),1);
    D = sqrt(sum(diff.^2,2));
    distMat(row_idx) = min(D);
end

SQ_pcl = mean(distMat);

% Distance from pcl to SQ
reference = SQ;
sample = segments.Location;

distMat = zeros(size(sample,1),1);
for row_idx = 1:size(sample,1)
    diff = reference-repmat(sample(row_idx,:),size(reference,1),1);
    D = sqrt(sum(diff.^2,2));
    distMat(row_idx) = min(D);
end

pcl_SQ = mean(distMat);

end