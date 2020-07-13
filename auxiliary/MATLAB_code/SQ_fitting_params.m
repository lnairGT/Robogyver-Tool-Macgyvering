%% Superellipsoid fitting to tool parts 
% 1) No bending or tapering parameters implemented yet 

% Input: "SEGMENTED" point cloud - currently using the Tool-Web dataset,
% type of SQ to fit
% Output: Best fit superquadrics 3D points

function [fit_params, fit_type, SQ, residue_SQ] = SQ_fitting_params(point_cloud, SQ_type)
    %% Fit segments using non-linear optimization

    segment_members = point_cloud.Location;
    segment_members_original = segment_members;

    for i = 1:1
        residue_SQ = inf;

        % Get segment transformed using PCA and the inverse transformation
        [segment_members, inv_pca] = pca_segment(segment_members);

        for j = 1:size(SQ_type,2)
            type = SQ_type(j);

            % Parameter Initialization for the segment
            [scale, orientations, eps, p, bound_min, bound_max] = param_init(segment_members, type);

            % Min and Max bounds for optimization based on the initial parameters
            min_bound = double([0.8*scale(1), 0.8*scale(2), 0.8*scale(3), 0.01, 0.1, 0.1,...
                -pi, -pi, -pi, bound_min(1), bound_min(2), bound_min(3)]);
            max_bound = double([1.2*scale(1), 1.2*scale(2), 1.2*scale(3), 1, 2.0, 2.0,...
                pi, pi, pi, bound_max(1), bound_max(2), bound_max(3)]); 

            % Initialize the 12 parameters for superquadrics
            x_init = double([scale(1), scale(2), scale(3), scale(4), eps(1),...
                eps(2), orientations(1), orientations(2), orientations(3),...
                p(1), p(2), p(3)]);

            % Levenberg-Marquardt optimization
            options = optimset('Display','off','TolX',1e-10,'TolFun',1e-10,'MaxIter',3000,'MaxFunEvals',3000); 
            [optimum_quadrics,~,~,~,~] = lsqnonlin(@(x) fitting_fn(x,segment_members,type), x_init, min_bound, max_bound, options);
            %optimum_quadrics = ga(@(x) fitting_fn(x,segment_members,type),length(x_init),[],[],[],[],min_bound, max_bound);
            %optimum_quadrics = x_init;

            % Ranking the SQs
            SQ = SQ2PCL(optimum_quadrics, type);
            SQ = SQ*inv_pca;
            [pcl_SQ_dist, SQ_pcl_dist] = pcl_dist(segment_members_original, SQ); %Same number of points?
            residue = pcl_SQ_dist + SQ_pcl_dist;

            if residue < residue_SQ
                SQ_optimum = optimum_quadrics;
                residue_SQ = residue;
                optimum_type = type;
            end
        end
    end

    %% Point cloud for optimum Superquadric
    
    for i = 1:1
        % Generate a SQ pcl from optimum_quadrics and apply inverse pca tform
        SQ = SQ2PCL(SQ_optimum, optimum_type);
        inv_pca = reshape(inv_pca,[3,3]);
        SQ = SQ*inv_pca;
    end
    
    [scale, orientations, eps, p, ~, ~] = param_init(SQ, optimum_type);
    
    if optimum_type(1) == 2 % Toroid
        fit_params = zeros(1,12);
        fit_params(1:4) = scale;
        fit_params(5:6) = eps;
        fit_params(7:9) = orientations; 
        fit_params(10:12) = p;
    else
        fit_params = zeros(1,11);
        fit_params(1:3) = scale(1:3);
        fit_params(4:5) = eps;
        fit_params(6:8) = orientations; 
        fit_params(9:11) = p;
    end
    
    fit_type = optimum_type;
    SQ = pointCloud(SQ);
end