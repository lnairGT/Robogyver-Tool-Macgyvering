# Training Prediction Models

This folder contains code for training the shape, material and attachment prediction models. Note that the code for both material and attachment predictions are in the `material-predict` folder. The training data is not available in this repository. 

**1) shape-predict**: This folder contains code for training the neural network for shape score prediction. The network takes ESF features as input to output the score indicating the fitness of the input point cloud for performing a specific action. For training the models, the data is available [HERE](https://github.com/NithinShrivatsav/Tool-Substitution-with-Shape-and-Material-ReasoningUsing-Dual-Neural-Networks) in the `data` folder. 

**2) material-predict**: This folder contains code for predicting material class of the objects from input spectral readings. For more details on this, we refer the reader to the SMM50 dataset and paper [https://github.com/Healthcare-Robotics/smm50](https://github.com/Healthcare-Robotics/smm50) for training the models. Additionally, the `learn.py` function has a `predictPierceability` setting that can be used to either train the model for pierce prediction or for material prediction. Both use the same SMM50 dataset for training. 
