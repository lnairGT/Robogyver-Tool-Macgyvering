'''
Author: Nithin Shrivatsav Srikanth, Lakshmi Nair
Description: This script is used to train the dual neural network for tool substitution with shape properties.
'''
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils import shuffle
from sklearn.externals import joblib
from sklearn.metrics import accuracy_score
import tensorflow as tf
from keras.models import Sequential, Model
from keras.layers import Dense, Input, Lambda, Dropout, merge
import keras.backend as K
from keras import optimizers
from keras import regularizers
from keras.utils import plot_model
import numpy as np
import pandas
import random
import os
import csv
import time

np.random.seed(11)

def sigmoid(z):
    return 1/(1+np.exp(-z))

## Function to create data pairs
def data_pairs_creation(data, data_pairs, n_classes):
    pairs = []
    index_pairs = []
    labels = []
    count_pos = 0.0
    count_neg = 0.0
    n = [len(data_pairs[d]) for d in range(len(n_classes))]
    for d in range(len(n_classes)):
        for i in range(int(n[d])):
            for j in range(i+1,int(n[d])):
                z1, z2 = data_pairs[d][i], data_pairs[d][j]
                pairs.append([data[z1],data[z2]])
                labels.append(1)
        #count_pos = count_pos + 1
                inc = random.randrange(1, len(n_classes))
                dn = (d+inc)%(len(n_classes))
                if j >= int(n[dn]):
                    continue
                else:
                    z1, z2 = data_pairs[d][i], data_pairs[dn][j]
                    pairs.append([data[z1],data[z2]])
                    index_pairs.append([z1,z2])
                    labels.append(0)
            #count_neg = count_neg + 1
    return np.array(pairs), np.array(labels)

if __name__ == "__main__":
    ## Read the dataset
    data = pandas.read_csv('/home/nithin/Desktop/Tool-Substitution-with-Shape-and-Material-ReasoningUsing-Dual-Neural-Networks/data/shape_data/scoop/esf_scoop_train.csv')
    Y = data.Label
    X = data.drop(['Object','Label'],axis=1)
    X, Y = shuffle(X, Y, random_state=1)
    X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=0.1,random_state=1)

    ## Preprocessing
    scaler = preprocessing.StandardScaler()
    scaler.fit(X_train)
    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)

    joblib.dump(scaler, '/home/nithin/Desktop/Tool-Substitution-with-Shape-and-Material-ReasoningUsing-Dual-Neural-Networks/models/shape/Scalar_wts/scaler_scoop.save')

    input_shape = X_train.shape[1:]

    n_classes,_ = np.unique(Y_train, return_counts=True, axis=0)

    ## Create the training and testing pairs
    training_pairs = [np.where(Y_train==i)[0] for i in n_classes]
    x_train, y_train = data_pairs_creation(X_train, training_pairs, n_classes)
    x_train, y_train = shuffle(x_train, y_train,random_state=1)

    testing_pairs = [np.where(Y_test==i)[0] for i in n_classes]
    x_test, y_test = data_pairs_creation(X_test, testing_pairs, n_classes)

    ## Build Model
    inputs = Input(input_shape)
    x = Dense(100,  activation='tanh', kernel_regularizer=regularizers.l2(0.001),name='Features1')(inputs)
    x = Dropout(0.5)(x)
    x = Dense(100,  activation='tanh', kernel_regularizer=regularizers.l2(0.001),name='Features2')(x)
    x = Dropout(0.5)(x)
    x = Dense(25,  activation='tanh', kernel_regularizer=regularizers.l2(0.001),name='Features3')(x)
    x = Dropout(0.5)(x)

    ## Base Network
    base_network = Model(inputs=inputs, outputs=x)

    ## Create the inputs
    input_features_1 = Input(input_shape)
    input_features_2 = Input(input_shape)

    ## Tool Encodings
    tool_encoding_1 = base_network(input_features_1)
    tool_encoding_2 = base_network(input_features_2)

    ## Similarity Layer
    l1_distance_layer = Lambda(lambda tensors: K.square(tensors[0]-tensors[1]), name='L1_Distance')
    l1_distance = l1_distance_layer([tool_encoding_1, tool_encoding_2])

    ## Distance Fusion and Final Prediction Layer
    prediction = Dense(1, activation='sigmoid', name='Final_Layer')(l1_distance)
    model = Model(inputs=[input_features_1, input_features_2], outputs=prediction)


    ## Compile and Fit the model
    model.compile(loss='binary_crossentropy', optimizer=optimizers.Adam(lr=0.0001), metrics=['binary_accuracy'])
    model.fit([x_train[:,0], x_train[:,1]], y_train, validation_split=0.2, epochs=4000, batch_size=100)
    model.save_weights('/home/nithin/Desktop/Tool-Substitution-with-Shape-and-Material-ReasoningUsing-Dual-Neural-Networks/models/shape/Model/model_weights_shape_scoop.h5')
    results = model.predict([x_test[:,0], x_test[:,1]])
    for i in range(results.shape[0]):
    	if results[i]>=0.5:
    		results[i] = 1
    	else:
    		results[i] = 0
    results = results.flatten()
    print(classification_report(y_test,results))
    print(confusion_matrix(y_test,results))

    ## Create Embeddings
    embedding_data = pandas.read_csv('/home/nithin/Desktop/Tool-Substitution-with-Shape-and-Material-ReasoningUsing-Dual-Neural-Networks/data/shape_data/scoop/esf_scoop_embeddings.csv')
    embedding_inputs = embedding_data.drop(['Object'],axis=1)
    print(embedding_inputs.shape)
    embedding_inputs = scaler.transform(embedding_inputs)
    embedding_outputs = base_network.predict(embedding_inputs)
    np.save('/home/nithin/Desktop/Tool-Substitution-with-Shape-and-Material-ReasoningUsing-Dual-Neural-Networks/models/shape/Embeddings/embeddings_shape_scoop.npy',embedding_outputs)
