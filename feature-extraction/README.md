# Extracting ESF Features from Point Clouds

This folder contains C++ code for computing ESF, SHOT-C and SHOT-A features. We use PCL's existing functions to do this. Each code takes in a folder that stores point clouds for which the features need to be computed. Once the features are computed, they are saved onto .csv files.

In my thesis, I found ESF features to work really well. So my final pipeline uses ESF features for shape scoring. However, I've included the SHOT features for completeness. 

**1) ESF features**

This is a 640-D vector of values that represents the shape of the point cloud. See **W. Wohlkinger and M. Vincze, "Ensemble of shape functions for 3D object classification,"** 
2011 IEEE International Conference on Robotics and Biomimetics, Karon Beach, Phuket, 2011, pp. 2987-2992, doi: 10.1109/ROBIO.2011.6181760.

For more details on the application of the different features for tool construction, see my paper **Nair, Lakshmi, et al. "Autonomous Tool Construction Using Part Shape and Attachment Prediction."**
Robotics: Science and Systems. 2019.

**2) Material: SCiO features**

For the material prediction, we use a handheld spectrometer that outputs a 331-D vector of real values indicating spectral intensities. For more details on this work, please refer to Zackory Erickson's work with spectral sensing (SMM50 dataset), available at [https://github.com/Healthcare-Robotics/smm50](https://github.com/Healthcare-Robotics/smm50)

His paper: **Z. Erickson, N. Luskey, S. Chernova, and C. C. Kemp, "Classification of Household Materials via Spectroscopy"**, 
IEEE Robotics and Automation Letters (RA-L), 2019.



