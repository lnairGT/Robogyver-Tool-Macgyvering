This folder contains C++ code for computing ESF, SHOT-C and SHOT-A features. We use PCL's existing functions to do this. 

In my thesis, I found ESF features to work really well. So my final pipeline uses ESF features for shape scoring. However, I've included the SHOT features for completeness. 

**ESF features**

This is a 640-D vector of values that represents the shape of the point cloud. See **W. Wohlkinger and M. Vincze, "Ensemble of shape functions for 3D object classification,"** 
2011 IEEE International Conference on Robotics and Biomimetics, Karon Beach, Phuket, 2011, pp. 2987-2992, doi: 10.1109/ROBIO.2011.6181760.

For more details on the application of the different features for tool construction, see my paper **Nair, Lakshmi, et al. "Autonomous Tool Construction Using Part Shape and Attachment Prediction."**
Robotics: Science and Systems. 2019.




