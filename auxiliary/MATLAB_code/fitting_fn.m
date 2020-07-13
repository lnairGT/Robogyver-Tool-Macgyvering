%% Fitting function for superellipsoids

% Input - list of parameters for optimization - 11 parameters
% Output - Inside_Outside function score for how well segment points fit
%the superquadric

function cost = fitting_fn(opt_params, current_segment, SQ_type)

    pcl = current_segment;
    
    % Scaling parameters
    a1 = opt_params(1);
    a2 = opt_params(2);
    a3 = opt_params(3);
    a4 = opt_params(4);
    
    % Exponential terms that define the superquadric bending, roundness
    eps1 = opt_params(5);
    eps2 = opt_params(6);
    
    % In radians - Rotation about X, Y and Z axes
    angle_x = opt_params(7);
    angle_y = opt_params(8);
    angle_z = opt_params(9);
    
    % Translation along X, Y and Z axes (the last three parameters)
    trans_x = opt_params(end-2);
    trans_y = opt_params(end-1);
    trans_z = opt_params(end);
    
    % Apply Rotation and Translation to the Superquadric
    nx = cos(angle_x)*cos(angle_y)*cos(angle_z)-(sin(angle_x)*sin(angle_z));
    ny = sin(angle_x)*cos(angle_y)*cos(angle_z)+cos(angle_x)*sin(angle_z);
    nz = -(sin(angle_y)*cos(angle_z));
    ox = -(cos(angle_x)*cos(angle_y)*sin(angle_z))-(sin(angle_x)*cos(angle_z));
    oy = -(sin(angle_x)*cos(angle_y)*sin(angle_z))+cos(angle_x)*cos(angle_z);
    oz = sin(angle_y)*sin(angle_z);
    ax = cos(angle_x)*sin(angle_y);
    ay = sin(angle_x)*sin(angle_y);
    az = cos(angle_y);   
    X = (nx*pcl(:,1)+ny*pcl(:,2)+nz*pcl(:,3)-trans_x*nx-trans_y*ny-trans_z*nz);
    Y = (ox*pcl(:,1)+oy*pcl(:,2)+oz*pcl(:,3)-trans_x*ox-trans_y*oy-trans_z*oz);
    Z = (ax*pcl(:,1)+ay*pcl(:,2)+az*pcl(:,3)-trans_x*ax-trans_y*ay-trans_z*az);

    % Scale the ellipsoid
    X = X./a1;
    Y = Y./a2;
    Z = Z./a3;    

    if SQ_type == 0 || SQ_type == 1
        % The inside-outside function of an ellipsoid and hyperparaboloid
        quadric_func = (abs(X.^(2/eps2))+abs(Y.^(2/eps2))).^(eps2/eps1)+(abs(Z.^(2/eps1)));
        
    elseif SQ_type == 2
        % The inside-outside function of a toroid
        quadric_func = ((abs(X.^(2/eps2))+abs(Y.^(2/eps2))).^(eps2/2) - a4).^(2/eps1)+(abs(Z.^(2/eps1)));
        
    elseif SQ_type == 3
        % The inside-outside function of a paraboloid
        quadric_func = ((abs(X.^(2/eps2))+abs(Y.^(2/eps2))).^(eps2/eps1))-Z;
    else
        error("Incorrect type input");
    end
    
    % The Levenberg-Marquadt cost function using the inside-outside function
    cost = double((a1*a2*a3)*(abs(quadric_func.^eps1) - 1).^2);
   
end
