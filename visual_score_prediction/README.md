# Predicting Scores Using Pre-trained Models

This folder contains the code for predicting shape, material and attachment scores from pre-trained models. It takes features stored in csv files and predicts score using the pre-trained models:

- **pre-extracted-features**: This folder contains csv files that store ESF features for the 58 point clouds in the dataset (`pre-extracted-features\ESF_features`). It also contains the SCiO readings extracted for the different objects (`pre-extracted-features\unprocessed_SCiO_files`). These are used by the `score_predict.py` to compute shape and material scores.

- **pre-trained-models**: This folder contains pre-trained models for shape, material and attachment predictions, specifically pierce attachment prediction. Note that we train independent shape models for each tool type, hence the separate joblib files in `pre-trained-models\Shape_models`. For material prediction, we have a single model that performs multi-classification to predict the material class of the objects (`pre-trained-models\Material_models`). The .json and .h5 files describe the model and its weights. For attachment prediction, our work considers three types of attachments: magnets, pierce attachments and grasp attachments. We assume that magnet locations are provided a-priori. For pierce and grasp attachment prediction, we use the following:
  - **Pierce attachment**: The model is provided in `pre-trained-models\Pierce_models`. The .json and .h5 files describe the model and its weights. They take a SCiO reading as input and output a binary label indicating whether the material is pierceable. 
  - **Grasp attachment**: To predict locations where objects can be grasped, we use the work developed by **Andreas ten Pas, Marcus Gualtieri, Kate Saenko, and Robert Platt. Grasp Pose Detection in Point Clouds.**, The International Journal of Robotics Research, Vol 36, Issue 13-14, pp. 1455-1473. October 2017. You can find their code [HERE](https://github.com/atenpas/gpd). We store whether objects can be grasped and their grasp locations onto csv files. You will find this information in the file `num_att.csv`. This file contains the number of grasps that are sampled for the 58 object point clouds using the approach. The file also specifies whether magnets are present on the objects. 
  
 - `score_predict.py`: This file uses the pre-trained models and pre-extracted features to compute the shape, material and attachment scores for each object, and store them in csv files. It also includes code for reading from the different csv files. Once the files are placed in appropriate directories, `score_predict.py` can be directly run without any additional requirements. Descriptions for each of the functions is available within the code. 
 
 
 
 
