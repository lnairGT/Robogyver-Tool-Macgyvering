'''
Author: Nithin Shrivatsav Srikanth, Lakshmi Nair
Acknowledgment: Derived some functions from Zackory Erickson's work
Description: This script is used to train the dual neural network for tool substitution with material properties.
'''
import os, sys
import numpy as np
import cPickle as pickle
import csv

import keras
from keras.models import Sequential, Model
from keras.layers import Dense, Input, Lambda, Dropout, merge, MaxPooling1D, Flatten, Conv1D
import keras.backend as K
from keras import optimizers
from keras import regularizers
from keras.utils import plot_model
from keras.utils.np_utils import to_categorical

from sklearn.preprocessing import Normalizer, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils import shuffle
from sklearn.externals import joblib
from sklearn.metrics import accuracy_score

import random

def sigmoid(z):
  return 1/(1+np.exp(-z))

def features_scio(csv_file):
	# Take csv file and retrieve scio_processed_data corresponding to input
	features = {}
	obj_materials = {}
	wavelengthCount = 331
	with open(csv_file) as f:
		reader = csv.reader(f)
		for idx, row in enumerate(reader):
			if idx == 10:
				wavelengths = [float(r.strip().split('_')[-1].split()[0]) + 740.0 for r in row[10:wavelengthCount+10]]
			try:
				int(row[0]) # To skip first few rows until first integer encountered
				if '.ply' not in row[3]:
					obj_name = row[3] + '.ply'
				else:
					obj_name = row[3]
				features_list = [float(elt) for elt in row[10:wavelengthCount+10]]
				features_list = firstDeriv(features_list, wavelengths)
				features[obj_name] = features_list

				material_name = row[4]
				obj_materials[obj_name] = row[4]
			except:
				pass

	return features, obj_materials

def loadScioDataset(pklFile, csvFile, materialNames=[], objectNames=[]):
  saveFilename = pklFile + '.pkl'
  if os.path.isfile(saveFilename):
    with open(saveFilename, 'rb') as f:
      X, y_materials, y_objects, wavelengths = pickle.load(f)

  else:
    X = []
    y_materials = []
    y_objects = []
    filename = csvFile + '.csv'
    print(filename)
    wavelengthCount = 331
    with open(filename, 'rb') as f:
      reader = csv.reader(f)
      for i, row in enumerate(reader):
        if i < 10 or i == 11:
          continue
        if i == 10:
          # Header row
          wavelengths = [float(r.strip().split('_')[-1].split()[0]) + 740.0 for r in row[10:wavelengthCount+10]]
          continue
        obj = row[3].strip()
        material = row[4].strip()
        if material not in materialNames:
          continue
        index = materialNames.index(material)
        if objectNames is not None and obj not in objectNames[index]:
          continue
        values = [float(v) for v in row[10:wavelengthCount+10]]
        X.append(values)
        y_materials.append(index)
        y_objects.append(obj)

        with open(saveFilename, 'wb') as f:
          pickle.dump([X, y_materials, y_objects, wavelengths], f, protocol=pickle.HIGHEST_PROTOCOL)
  return X, y_materials, y_objects, wavelengths

def firstDeriv(x, wavelengths):
  # First derivative of measurements with respect to wavelength
  x = np.copy(x)
  for i, xx in enumerate(x):
    dx = np.zeros(xx.shape, np.float)
    dx[0:-1] = np.diff(xx)/np.diff(wavelengths)
    dx[-1] = (xx[-1] - xx[-2])/(wavelengths[-1] - wavelengths[-2])
    x[i] = dx
  return x


## Function to create data pairs
def data_pairs_creation(data, data_pairs, n_classes):
    pairs = []
    labels = []
    n = [len(data_pairs[d]) for d in range(len(n_classes))]
    for i in range(int(n[1])):
      for j in range(i+1,int(n[1])):
        z1, z2 = data_pairs[1][i], data_pairs[1][j]
        pairs.append([data[z1],data[z2]])
        labels.append(1)
        if j >= int(n[0]):
            continue
        else:
            z3, z4 = data_pairs[1][i], data_pairs[0][j]
            pairs.append([data[z3],data[z4]])
            labels.append(0)
    return np.array(pairs), np.array(labels)

# object_class = 'cut'
# object_class = 'flip'
# object_class = 'hit'
object_class = 'poke'
# object_class = 'rake'
# object_class = 'scoop'

## Materials to be used
materials = ['plastic', 'paper', 'wood', 'metal', 'foam']

## Constitutent Classes of each material
plastics = ['HDPE', 'PET', 'polyethyleneBlue', 'polyethyleneGreen', 'polyethyleneRed', 'polyethyleneYellow', 'PP', 'PVC', 'thermoPolypropylene', 'thermoTeflon']
fabrics = ['cottonCanvas', 'cottonSweater', 'cottonTowel', 'denim', 'felt', 'flannel', 'gauze', 'linen', 'satin', 'wool']
papers = ['cardboard', 'constructionPaperGreen', 'constructionPaperOrange', 'constructionPaperRed', 'magazinePaper', 'newspaper', 'notebookPaper', 'printerPaper', 'receiptPaper', 'textbookPaper']
woods = ['ash', 'cherry', 'curlyMaple', 'hardMaple', 'hickory', 'redCedar', 'redElm', 'redOak', 'walnut', 'whiteOak']
metals = ['aluminum', 'aluminumFoil', 'brass', 'copper', 'iron', 'lead', 'magnesium', 'steel', 'titanium', 'zinc']
objects = [plastics, fabrics, papers, woods, metals]

foam = ['styrofoam_cup', 'ball', 'pie', 'dinosaur_yellow', 'dinosaur_blue', 'dinosaur_purple', 'dinosaur_green', 'dinosaur_orange', 'toad_mario', 'baseball', 'white_sheets', 'black_sheets', 'styrofoam_block', 'sandal']
objects2 = [[], [], [], [], [], foam]

# print len(plastics), len(fabrics), len(woods), len(metals), len(papers), len(foam)

saveFilename = 'smm50_scio.pkl'
with open(saveFilename, 'rb') as f:
    X, y_materials, y_objects, wavelengths = pickle.load(f)

not_fabrics_indices = [i for i,x in enumerate(y_objects) if x not in fabrics]
X_new_no_fabric = [x for i,x in enumerate(X) if i in not_fabrics_indices]
y_objects_new_no_fabric = [x for i,x in enumerate(y_objects) if i in not_fabrics_indices]
y_materials_new_no_fabric = [x for i,x in enumerate(y_materials) if i in not_fabrics_indices]
X = X_new_no_fabric
y_materials = y_materials_new_no_fabric
y_objects = y_objects_new_no_fabric

X2, y_materials2, y_objects2, _ = loadScioDataset(pklFile='scio_everyday_objects_expanded', csvFile='scio_everyday_objects_expanded', materialNames=materials, objectNames=objects2)

## Print the class of foam and metal, wood, plastic, fabric, paper 
#print(y_materials2) 
#print(y_materials)
# print np.shape(X), np.shape(y_materials), np.shape(y_objects), np.shape(X2), np.shape(y_materials2), np.shape(y_objects2)

## Combine the foam with the other classes
X = np.concatenate([X, X2], axis=0)
y_materials = np.concatenate([y_materials, y_materials2], axis=0)
y_objects = np.concatenate([y_objects, y_objects2], axis=0)
wavelengths = np.array(wavelengths)
# np.save('wavelengths.npy',wavelengths)
# print np.shape(X), np.shape(y_materials), np.shape(y_objects), np.shape(X2), np.shape(y_materials2), np.shape(y_objects2)

## Form a dataset with just a few samples of each subclass of the main class
samples = 50
X_new = []
y_materials_new = []
y_objects_new = []
for x, ym, yo in zip(X, y_materials, y_objects):
    # print yo, len(y_objects_new[y_objects_new == yo]), len(y_objects)
    if yo not in y_objects_new or len(np.array(y_objects_new)[np.array(y_objects_new) == yo]) < samples:
        X_new.append(x)
        y_materials_new.append(ym)
        y_objects_new.append(yo)

X = X_new
y_materials = y_materials_new
y_objects = y_objects_new

# print np.shape(X), np.shape(y_materials), np.shape(y_objects)

## The final train and test set after preprocessing
X = firstDeriv(X, wavelengths)
Y = np.array(y_materials)

Y[Y==0]=6 ## Plastic
Y[Y==2]=7 ## Paper
Y[Y==3]=8 ## Wood
Y[Y==4]=9 ## Metal
Y[Y==5]=10 ## Foam

if object_class == 'cut':
    Y[Y==6] = 1
    Y[Y==7] = 0
    Y[Y==8] = 1
    Y[Y==9] = 1
    Y[Y==10] = 0
elif object_class =='flip':
    Y[Y==6] = 0
    Y[Y==7] = 0
    Y[Y==8] = 1
    Y[Y==9] = 1
    Y[Y==10] = 0
elif object_class == 'hit':
    Y[Y==6] = 0
    Y[Y==7] = 0
    Y[Y==8] = 1
    Y[Y==9] = 1
    Y[Y==10] = 0
elif object_class == 'poke':
    Y[Y==6] = 1
    Y[Y==7] = 0
    Y[Y==8] = 0
    Y[Y==9] = 1
    Y[Y==10] = 0
elif object_class == 'rake':
    Y[Y==6] = 1
    Y[Y==7] = 0
    Y[Y==8] = 1
    Y[Y==9] = 0
    Y[Y==10] = 0
elif object_class == 'scoop':
    Y[Y==6] = 1
    Y[Y==7] = 0
    Y[Y==8] = 1
    Y[Y==9] = 1
    Y[Y==10] = 0

## Preprocessing
scaler = StandardScaler()
scaler.fit(X)
X = scaler.transform(X)
input_shape = X.shape[1:]

## Save the StandardScaler object for use during testing
scaler_filename = '/home/nithin/Desktop/Tool-Substitution-with-Shape-and-Material-ReasoningUsing-Dual-Neural-Networks/models/material/Scalar_wts/scaler_materials_big_new_poke.save'
joblib.dump(scaler, scaler_filename)

## Create the Training and Testing Pairs
n_classes,_ = np.unique(Y, return_counts=True, axis=0)

training_pairs = [np.where(Y==i)[0] for i in n_classes]
x_train, y_train = data_pairs_creation(X, training_pairs, n_classes)
x_train, y_train = shuffle(x_train, y_train,random_state=1)

## Build Model
input = Input(input_shape)
x = Dense(426,  activation='tanh', kernel_regularizer=regularizers.l2(0.001),name='Features1')(input)
x = Dropout(0.5)(x)
x = Dense(284,  activation='tanh', kernel_regularizer=regularizers.l2(0.001),name='Features2')(x)
x = Dropout(0.5)(x)
x = Dense(128,  activation='tanh', kernel_regularizer=regularizers.l2(0.001), name='Features3')(x)
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
model.compile(loss='binary_crossentropy', optimizer=optimizers.Adam(lr=0.001), metrics=['binary_accuracy'])
mc = keras.callbacks.ModelCheckpoint('poke_weights{epoch:08d}.h5', save_weights_only=True, period=10)
model.fit([x_train[:,0], x_train[:,1]], y_train, validation_split=0.2, epochs=10, batch_size=50, verbose=1, callbacks=[mc])
model.save_weights('/home/nithin/Desktop/Tool-Substitution-with-Shape-and-Material-ReasoningUsing-Dual-Neural-Networks/models/material/Model/material_prop_weights_big_new_poke.h5')

## Create Embeddings
embedding_data = np.copy(X)
embedding_data_label = np.copy(Y)
embedding_data_indices = [i for i,x in enumerate(embedding_data_label) if x == 1]
embedding_inputs_temp = [x for i,x in enumerate(embedding_data) if i in embedding_data_indices]
embedding_inputs = np.array(embedding_inputs_temp)
embedding_outputs = base_network.predict(embedding_inputs)
np.save('/home/nithin/Desktop/Tool-Substitution-with-Shape-and-Material-ReasoningUsing-Dual-Neural-Networks/models/material/Embeddings/poke_embeddings.npy', embedding_outputs)


