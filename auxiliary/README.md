This folder contains code that I developed during my thesis. They are not crucial to running the final pipeline, but I'm adding them here for anyone that might find them useful.

**NOTE**: This folder is not particularly maintained. However, there may be some functions that might be useful for other projects. 

I've described each folder/file in more detail below:

1) `nimbus_explore.py`: This folder includes the final framework for tool construction (See paper **Nair, Lakshmi, et al. "Autonomous Tool Construction Using Part Shape and Attachment Prediction."** 
Robotics: Science and Systems. 2019.) for more details. There are functions that compute shape, material, attachment scores, and take a weighted sum of these values for the final score that is used for tool construction.

2) `object_class.py`: This is used by `nimbus_explore.py`. Objects have associated material and attachment predictions.

3) `dual_NN.py`: This contains functions for using dual neural networks for predicting shape and material scores. It uses pre-trained models that are saved in the `models` folder. We used this work primarily for performing tool substitution. See our paper **Shrivatsav, Nithin, Lakshmi Nair, and Sonia Chernova. "Tool Substitution with Shape and Material Reasoning Using Dual Neural Networks."** 
arXiv preprint arXiv:1911.04521 (2019). The Github repository [HERE](https://github.com/NithinShrivatsav/Tool-Substitution-with-Shape-and-Material-ReasoningUsing-Dual-Neural-Networks) contains code and data for training the dual neural networks. 

4) `MATLAB_code`: Contains code that is adapted from work by **Abelha, Paulo, Frank Guerin, and Markus Schoeler. "A model-based approach to finding substitute tools in 3d vision data."** 2016 IEEE International Conference on Robotics and Automation (ICRA). IEEE, 2016. They use Superquadrics to represent object point clouds. We've adapted some of this work to tool construction. You can find more details and code in their repository [HERE](https://github.com/pauloabelha/enzymes). My code in this folder has additional files that can compute attachment scores as described in my papers. 

