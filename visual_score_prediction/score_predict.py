# python 2.7

#---- SCORE PREDICTION ----#

# geoscore_predict uses the trained models to predict whether the input ESF feature is appropriate for a specific action
# pierce_predict uses the trained models to predict whether the input SCiO reading is pierceable
# material_predict uses trained models to predict the material class of the input SCiO reading
# material_class maps the material class prediction to a score indicating material fitness for a specific action

#---- READING FEATURES FROM CSV FILES ----#

# ESF_retrieve reads the ESF features for the point clouds from a csv file
# object_sense retrieves *processed* SCiO readings for point clouds from csv file
# features_scio processes the raw input SCiO readings for the objects
# first_deriv is a step involved in processing the SCiO readings

# ---- WRITING FEATURES TO CSV ----#

# materials_write is used to write material scores to csv file

# NOTE -- Pre-trained models are available in the same folder

import os
from sklearn.externals import joblib
import numpy as np
import csv
import ast
#from keras.models import model_from_json
#import keras.backend as K

def geoscore_predict(obj_1, reference_action):
    if reference_action == 'hit':
        learning_file = 'ESF_NN_Hammer_Final.joblib'
    elif reference_action == 'scoop':
        learning_file = 'ESF_NN_Scoop_Final.joblib'
    elif reference_action == 'squeegee':
        learning_file = 'ESF_NN_Squeegee_Final.joblib'
    elif reference_action == 'flip':
        learning_file = 'ESF_NN_Spatula_Final.joblib'
    elif reference_action == 'screw':
        learning_file = 'ESF_NN_Screwdriver_Final.joblib'
    elif reference_action == 'rake':
        learning_file = 'ESF_NN_Rake_Final.joblib'
    elif reference_action == 'handle':
        learning_file = 'ESF_NN_Handles_Final.joblib'
    else:
        print("Unknown reference action specified \n")
        return None

    action_part = ESF_retrieve(obj_1)

    if action_part == None:
        print("ERROR: ESF features not found")

    joblib_location = r'C:\...\NN_joblib_files' # Path to the trained model

    model_action = joblib.load(os.path.join(joblib_location,learning_file))
    a_score = model_action.predict_proba(np.array(action_part).reshape(1, -1))
    action_score = a_score[0][1]

    geoscore = action_score
    return geoscore

def pierce_predict(obj_name):
    K.clear_session()
    trained_model = 'pierce_NN.json'
    trained_wts = 'pierce_wts.h5'

    scio_data_processed = object_sense(obj_name)

    json_file = open(trained_model, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)

    # load weights into new model
    loaded_model.load_weights(trained_wts)
    loaded_model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

    # Normalize the data
    scale = None #'scaler'  # No scaler performs better for the 5 class pierceability problem
    if scale is not None:
        scaler = Normalizer()
        obj = scaler.transform([scio_data_processed])
    else:
        obj = [scio_data_processed]
    pierce_value = loaded_model.predict_classes(np.array(obj))

    return pierce_value

def materials_predict(obj_name, reference_action):
    K.clear_session()
    trained_model = 'materials_NN.json'
    trained_wts = 'materials_wts.h5'

    scio_data_processed = object_sense(obj_name)
    json_file = open(trained_model, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights(trained_wts)
    loaded_model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
    mat_score = loaded_model.predict_proba(np.array([scio_data_processed]))

    if t == 'hit':
        idx = [1, 2] # Indicates the material classes appropriate for `hit' action
    elif t == 'scoop' or t == 'rake' or t == 'flip':
        idx = [0, 1, 2]
    elif t == 'squeegee':
        idx = [3]
    elif t == 'screw':
        idx = [0, 2]
    else:
        print("Incorrect tool type \n")
        return None

    mat_score = mat_score[0]
    mat_score = max([mat_score[i] for i in idx])
    mat_score = mat_score if mat_score >= 0.48 else 'inf'
    return mat_score

def materials_class(filename):
    obj_name = []
    obj_dict = {}
    tool_types = ['hit', 'scoop', 'rake', 'screw', 'squeegee', 'flip']
    materials_classifier = ['materials_NN.json', 'materials_wts.h5']

    with open(filename) as f:
        r = csv.reader(f)
        for row in r:
            obj_name.append(row[0])

    for obj in obj_name:
        print(obj)
        values = []
        for t in tool_types:
            if t == 'hit':
                idx = [1,2]
            elif t == 'scoop' or t == 'rake' or t == 'flip':
                idx = [0,1,2]
            elif t == 'squeegee':
                idx = [3]
            elif t == 'screw':
                idx = [0,2]

            val = materials_predict(obj, materials_classifier[0], materials_classifier[1])
            val = val[0]
            val = max([val[i] for i in idx])
            val = val if val >= 0.48 else 'inf'
            values.append(val)
        obj_dict[obj] = values

    material_write(obj_dict)

def ESF_retrieve(point_cloud, esf_file=None): # CHECK THIS ONE
	ESF = {}
	if esf_file is None:
		ESF_file = 'esf_descriptors_final_DS.csv' # Specify new ESF file
	else:
		ESF_file = esf_file

	with open(ESF_file) as f:
		reader = csv.reader(f)
		next(reader)
		for idx, row in enumerate(reader):
			if row[0] == point_cloud:
				ESF_features = [ast.literal_eval(row[i+1]) for i in range(0,640)]
				return ESF_features

	return None

def object_sense(obj_name, obj_pose=None):
	#MG_dataset = 'Macgyver_DS_full.csv' # Should be MG_DS_all_objects.csv - Dataset used for RSS project
	MG_dataset = 'SCiO_finalDS_unprocessed.csv'

	scio_features = features_scio(MG_dataset)

	if obj_name not in scio_features.keys():
		print("Object not found: %s" %(obj_name))
		return None
	else:
		return scio_features[obj_name]


def features_scio(csv_file):
    # Take csv file and retrieve scio_processed_data corresponding to input
    features = {}
    wavelengthCount = 331
    with open(csv_file) as f:
        reader = csv.reader(f)
        for idx, row in enumerate(reader):
            if idx == 10:
                wavelengths = [float(r.strip().split('_')[-1].split()[0]) + 740.0 for r in row[10:wavelengthCount + 10]]
            try:
                int(row[0])  # To skip first few rows until first integer encountered
                if '.ply' not in row[4]:
                    obj_name = row[4] + '.ply'
                else:
                    obj_name = row[4]
                features_list = [float(elt) for elt in row[10:wavelengthCount + 10]]
                features_list = firstDeriv(features_list, wavelengths)
                features[obj_name] = features_list
            except:
                pass

    return features

def firstDeriv(x, wavelengths):
    # First derivative of measurements with respect to wavelength
    x = [np.copy(x)]
    for i, xx in enumerate(x):
        dx = np.zeros(xx.shape, np.float)
        dx[0:-1] = np.diff(xx) / np.diff(wavelengths)
        dx[-1] = (xx[-1] - xx[-2]) / (wavelengths[-1] - wavelengths[-2])
        x[i] = dx
    return x[0]

def material_write(obj_dict):
    with open('material_class.csv', 'wb') as f:
        w = csv.writer(f)
        for key, val in obj_dict.items():
            w.writerow([key, val])

########################################################################################################################

'''
# Use the functions above and save the predicted values into a .csv file to use with the task planner

obj_dict = {}
for obj in obj_name:
    print(obj)
    value = pierce_predict(obj)
    print(value[0])
    obj_dict[obj] = value[0]

with open('pierce.csv', 'w', newline='') as f:
    w = csv.writer(f)
    for key, val in obj_dict.items():
        w.writerow([key, val])'''

