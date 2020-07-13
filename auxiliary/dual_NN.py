from sklearn.externals import joblib
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.preprocessing import Normalizer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
#from plot_confusion_matrix import plot_confusion_matrix

import csv
import ast
import numpy as np
import random
import os
import util
from matplotlib import pyplot as plt
from os import path
import os.path

from keras.models import model_from_json
from keras.models import Sequential, Model, load_model
from keras.layers import Dense, Input, Lambda, merge, Dropout
import keras.backend as K
from keras import optimizers
from keras import regularizers

def sigmoid(z):
    return 1/(1+np.exp(-z))

def pierce_predict(scio_data_processed, trained_model, trained_wts):
    K.clear_session()
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

    return pierce_value # Potentially return the prediction score or probability as well?

def materials_predict(scio_data_processed, trained_model, trained_wts):
    K.clear_session()
    json_file = open(trained_model, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights(trained_wts)
    loaded_model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
    material_class = loaded_model.predict_classes(np.array([scio_data_processed]))

    return material_class 

def shape_dualNN(ESF, reference_action):
    K.clear_session()

    trained_embeddings_folder = '' # Location of embeddings
    trained_wts_folder = '' # Location of weights
    trained_scaler_folder = '' # Location of scalar weights

    trained_embeddings = trained_embeddings_folder + 'embeddings_shape_' + reference_action + '.npy'
    trained_wts = trained_wts_folder + 'model_weights_shape_' + reference_action + '.h5'
    scaler_file = trained_scaler_folder + 'scaler_' + reference_action + '.save'

    old_tool_encoding_full = np.load(trained_embeddings)
    old_tool_encoding = np.mean(old_tool_encoding_full,axis=0)
    old_tool_encoding = old_tool_encoding.reshape(old_tool_encoding.shape[0],1)
    ESF_processed = np.array([ESF])

    scale = 'scaler' #'scaler' #'scaler' or None
    if scale is not None:
        scaler = joblib.load(scaler_file)
        ESF_processed = scaler.transform(ESF_processed)
        input_shape = ESF_processed.shape[1:]
    else:
        input_shape = ESF_processed.shape[1:]

    if not path.exists('model_constr.json') or not path.exists('base_constr.json'):
         ## create the model
        input = Input(input_shape)
        x = Dense(100,  activation='tanh', kernel_regularizer=regularizers.l2(0.001),name='Features1')(input)
        x = Dropout(0.5)(x)
        x = Dense(100,  activation='tanh', kernel_regularizer=regularizers.l2(0.001),name='Features2')(x)
        x = Dropout(0.5)(x)
        x = Dense(25,  activation='tanh', kernel_regularizer=regularizers.l2(0.001), name='Features3')(x)
        x = Dropout(0.5)(x)

        ## Base Network
        base_network = Model(inputs=input, outputs=x)

        ## Create the inputs
        input_features_1 = Input(input_shape)
        input_features_2 = Input(input_shape)

        ## Tool Encodings
        tool_encoding_1 = base_network(input_features_1)
        tool_encoding_2 = base_network(input_features_2)

        ## Similarity Layer
        l1_distance_layer = Lambda(lambda tensors: K.abs(tensors[0]-tensors[1]), name='L1_Distance')
        l1_distance = l1_distance_layer([tool_encoding_1, tool_encoding_2])

        ## Distance Fusion and Final Prediction Layer
        prediction = Dense(1, activation='sigmoid', name='Final_Layer')(l1_distance)
        model = Model(inputs=[input_features_1, input_features_2], outputs=prediction)

        ## Compile and Fit the model
        model.compile(loss='binary_crossentropy', optimizer=optimizers.Adam(lr=0.0001), metrics=['binary_accuracy'])

        # Save model for faster processing
        model_json = model.to_json()
        with open("model_constr.json", "w") as json_file:
            json_file.write(model_json)

        base_json = base_network.to_json()
        with open("base_constr.json", "w") as base_file:
            base_file.write(base_json)

    else:
        json_file = open('model_constr.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)

        base_file = open('base_constr.json', 'r')
        loaded_base = base_file.read()
        base_file.close()
        base_network = model_from_json(loaded_base)

    model.load_weights(trained_wts)

    ## Test new data point
    tool_features = ESF_processed.reshape((1,640))
    new_tool_encoding = base_network.predict(tool_features)

    ## Calculate the L1 distance betweent the test embedding and trained embedding
    l1_distance_new_layer = np.absolute(new_tool_encoding.T-old_tool_encoding)

    ## Load the weights of the required layers
    layer_dict = dict([(layer.name, layer) for layer in model.layers])
    #weights_fusion_layer = layer_dict['Fusion'].get_weights()
    weights_final_layer = layer_dict['Final_Layer'].get_weights()
    #weights_fusion_layer = np.array(weights_fusion_layer)
    weights_final_layer = np.array(weights_final_layer)

    z2 = np.dot(l1_distance_new_layer.T, weights_final_layer[0]) + weights_final_layer[1]
    a2 = sigmoid(z2)

    return a2[0][0] #Probability of successful match

def materials_dualNN(scio_data_processed, trained_embeddings, trained_wts, scaler_file):
    K.clear_session()
    old_tool_encoding_full = np.load(trained_embeddings)
    old_tool_encoding = np.mean(old_tool_encoding_full,axis=0)
    old_tool_encoding = old_tool_encoding.reshape(old_tool_encoding.shape[0],1)
    scio_data_processed = np.array([scio_data_processed])

    scale = 'scaler' #'scaler' #'scaler' or None
    if scale is not None:
        scaler = joblib.load(scaler_file)
        scio_data_processed = scaler.transform(scio_data_processed)
        input_shape = scio_data_processed.shape[1:]
    else:
        input_shape = scio_data_processed.shape[1:]

    #print "Array shape is: \n"
    #print scio_data_processed.shape[1]

    if not path.exists('model.json') or not path.exists('base.json'):
         ## create the model
        input = Input(input_shape)
        x = Dense(426,  activation='tanh', kernel_regularizer=regularizers.l2(0.001),name='Features1')(input)
        x = Dropout(0.5)(x)
        x = Dense(284,  activation='tanh', kernel_regularizer=regularizers.l2(0.001),name='Features2')(x)
        x = Dropout(0.5)(x)
        x = Dense(128,  activation='tanh', kernel_regularizer=regularizers.l2(0.001), name='Features3')(x)
        x = Dropout(0.5)(x)
        #x = Dense(426,  activation='relu', kernel_regularizer=regularizers.l2(0.001),name='Features1')(input)
        #x = Dense(284,  activation='relu', kernel_regularizer=regularizers.l2(0.001),name='Features2')(x)
        #x = Dense(128,  activation='relu', kernel_regularizer=regularizers.l2(0.001), name='Features3')(x)

        ## Base Network
        base_network = Model(inputs=input, outputs=x)

        ## Create the inputs
        input_features_1 = Input(input_shape)
        input_features_2 = Input(input_shape)

        ## Tool Encodings
        tool_encoding_1 = base_network(input_features_1)
        tool_encoding_2 = base_network(input_features_2)

        ## Similarity Layer
        l1_distance_layer = Lambda(lambda tensors: K.abs(tensors[0]-tensors[1]), name='L1_Distance')
        l1_distance = l1_distance_layer([tool_encoding_1, tool_encoding_2])

        ## Distance Fusion and Final Prediction Layer
        #fusion_layer = Dense(64, activation='relu', kernel_regularizer=regularizers.l2(0.001), name='Fusion')(l1_distance)
        prediction = Dense(1, activation='sigmoid', name='Final_Layer')(l1_distance) #(fusion_layer)
        model = Model(inputs=[input_features_1, input_features_2], outputs=prediction)

        ## Compile and Fit the model
        model.compile(loss='binary_crossentropy', optimizer=optimizers.Adam(lr=0.001), metrics=['binary_accuracy'])

        # Save model for faster processing
        model_json = model.to_json()
        with open("model.json", "w") as json_file:
            json_file.write(model_json)

        base_json = base_network.to_json()
        with open("base.json", "w") as base_file:
            base_file.write(base_json)

    else:
        json_file = open('model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)

        base_file = open('base.json', 'r')
        loaded_base = base_file.read()
        base_file.close()
        base_network = model_from_json(loaded_base)

    model.load_weights(trained_wts)

    ## Test new data point
    tool_features = scio_data_processed.reshape((1,331))
    new_tool_encoding = base_network.predict(tool_features)

    ## Calculate the L1 distance betweent the test embedding and trained embedding
    l1_distance_new_layer = np.absolute(new_tool_encoding.T-old_tool_encoding)

    ## Load the weights of the required layers
    layer_dict = dict([(layer.name, layer) for layer in model.layers])
    #weights_fusion_layer = layer_dict['Fusion'].get_weights()
    weights_final_layer = layer_dict['Final_Layer'].get_weights()
    #weights_fusion_layer = np.array(weights_fusion_layer)
    weights_final_layer = np.array(weights_final_layer)

    ## Compute the prediction of last layer using Knn
    #z1 = np.dot(l1_distance_new_layer.T,weights_fusion_layer[0]) + weights_fusion_layer[1]
    #a1 = np.maximum(z1,0)
    #z2 = np.dot(a1,weights_final_layer[0]) + weights_final_layer[1]
    #a2 = sigmoid(z2)

    z2 = np.dot(l1_distance_new_layer.T, weights_final_layer[0]) + weights_final_layer[1]
    a2 = sigmoid(z2)

    return a2[0][0] #Probability of successful match

def features_scio(csv_file):
    # Take csv file and retrieve scio_processed_data corresponding to input
    features = {}
    wavelengthCount = 331
    with open(csv_file) as f:
        reader = csv.reader(f)
        for idx, row in enumerate(reader):
            if idx == 10:
                wavelengths = [float(r.strip().split('_')[-1].split()[0]) + 740.0 for r in row[10:wavelengthCount+10]]
            try:
                int(row[0]) # To skip first few rows until first integer encountered
                if '.ply' not in row[4]:
                    obj_name = row[4] + '.ply'
                else:
                    obj_name = row[4]
                features_list = [float(elt) for elt in row[10:wavelengthCount+10]]
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
        dx[0:-1] = np.diff(xx)/np.diff(wavelengths)
        dx[-1] = (xx[-1] - xx[-2])/(wavelengths[-1] - wavelengths[-2])
        x[i] = dx
    return x[0]