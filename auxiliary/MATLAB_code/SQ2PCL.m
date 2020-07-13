%% Function to plot the Superquadric as a point cloud

% Input - optimized parameters for all superquadrics
% Output - point cloud segments corresponding to each superquadric 

function [pcl_segments] = SQ2PCL(params,SQ_type)
    n = 50; %Number of points in the superquadric point cloud
    
    a1 = params(1);
    a2 = params(2);
    a3 = params(3);
    
    if length(params) > 11
        a4 = params(4);
        eps1 = params(5);
        eps2 = params(6);
    else
        eps1 = params(4);
        eps2 = params(5);
    end        
    
%          if a1/a2 < a2/a3
%              z_scale = a1;
%              a1 = a3;
%              a3 = z_scale;
%          end

    angle_x = params(end-5);
    angle_y = params(end-4);
    angle_z = params(end-3);
    
    trans_x = params(end-2);
    trans_y = params(end-1);
    trans_z = params(end);

    if SQ_type == 0
        % Initialize meshgrid for superellipsoid
        eta=linspace(-pi/2,pi/2,n);
        omega=linspace(-pi,pi,n);
        [X,Y]=meshgrid(eta,omega);

        X_surf = a1.*sign(cos(X)).*(abs(cos(X)).^eps1).*sign(cos(Y)).*(abs(cos(Y)).^eps2);
        Y_surf = a2.*sign(cos(X)).*(abs(cos(X)).^eps1).*sign(sin(Y)).*(abs(sin(Y)).^eps2);
        Z_surf = a3.*sign(sin(X)).*(abs(sin(X)).^eps1);
    
    elseif SQ_type == 1
        % Hyperboloid equation
        eta = linspace(-pi/2-1,pi/2-1,n); %Not inclusive of -pi/2 ad pi/2
        omega = linspace(-pi,pi,n);
        [X,Y] = meshgrid(eta,omega);

        X_surf = a1.*sign(sec(X)).*(abs(sec(X)).^eps1).*sign(cos(Y)).*(abs(cos(Y)).^eps2);
        Y_surf = a2.*sign(sec(X)).*(abs(sec(X)).^eps1).*sign(sin(Y)).*(abs(sin(Y)).^eps2);
        Z_surf = a3.*sign(tan(X)).*(abs(tan(X)).^eps1);
    
    elseif SQ_type == 2
        % Toroid equation
        eta = linspace(-pi,pi,n);
        [X,Y] = meshgrid(eta,eta);

        X_surf = a1.*(sign(cos(X)).*(abs(cos(X)).^eps1)+ a4).*sign(cos(Y)).*(abs(cos(Y)).^eps2);
        Y_surf = a2.*(sign(cos(X)).*(abs(cos(X)).^eps1)+ a4).*sign(sin(Y)).*(abs(sin(Y)).^eps2);
        Z_surf = a3.*sign(sin(X)).*(abs(sin(X)).^eps1);
    
    elseif SQ_type == 3
        % Paraboloid equation
        eta=linspace(0,1,n);
        omega=linspace(-pi,pi,n);
        [X,Y]=meshgrid(eta,omega);

        X_surf = a1.*X.*sign(cos(Y)).*(abs(cos(Y)).^eps2);
        Y_surf = a2.*X.*sign(sin(Y)).*(abs(sin(Y)).^eps2);
        Z_surf = a3.*((X.^(2/eps1))-1); % Paraboloid cuts ellipsoid in half
        %trans_x = trans_x + a3;
        %k = 2*params(9);
    else   
        error("Incorrect type input");
    end
    
    %%
        
    % Create a surface plot and extract corresponding 3D data
    %pcl_surf = surf(X_surf, Y_surf, Z_surf);
    %pcl_SQ = pointCloud([pcl_surf.XData(:), pcl_surf.YData(:), pcl_surf.ZData(:)]);
    pcl_SQ = pointCloud([X_surf(:), Y_surf(:), Z_surf(:)]); 
    
    % Rotate, translate superquadric based on optimized parameters
    rt_mat = makehgtform('translate', [trans_x, trans_y, trans_z], 'xrotate', angle_x, ...
            'yrotate', angle_y, 'zrotate', angle_z);
    rt_mat = affine3d(rt_mat');
    pcl_SQ = pctransform(pcl_SQ, rt_mat);
        
    % Save the 3D transformed points
    pcl_segments = pcl_SQ.Location;

end