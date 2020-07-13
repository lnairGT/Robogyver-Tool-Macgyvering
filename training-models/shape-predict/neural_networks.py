import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn import preprocessing
from sklearn.externals import joblib


## filename is the location of object descriptors extracted using ESF; labeled by 1 or 0 corresponding to their function
## We use separate datasets for each function
filename = '../ESF_train_hit.csv' #'../ESF_train_scoop.csv'

## Read the filename and drop the last column as it contains NaN values
data = pandas.read_csv(filename)
# data.drop(data.columns[len(data.columns)-1], axis=1, inplace=True)
# print(data)

## Get the labels
Y = data.Label
X = data.drop(['Function','S.No','Object Type','Names','Label'],axis=1)

## Shuffle the dataset and split it into training and testing set
X,Y = shuffle(X,Y,random_state=1)
# X = X.values
# Y = Y.values
X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=0.2,random_state=1)

## Number of training and testing samples
m_train = X_train.shape[0]
m_test = X_test.shape[0]
print("Training Size: "+str(m_train))
print("Test Size: "+str(m_test))

## Number of labels
n = 7
print("Number of Labels: "+str(n))

## preprocessing
scaler = StandardScaler()
scaler.fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

oneHotEncoding = preprocessing.LabelEncoder()
Y_train = oneHotEncoding.fit_transform(Y_train)
Y_test = oneHotEncoding.fit_transform(Y_test)

## Neural Network model
mlp = MLPClassifier(hidden_layer_sizes=(230,),max_iter=1000)
mlp.fit(X_train,Y_train)
predictions = mlp.predict(X_test)
print(confusion_matrix(Y_test,predictions))
print(classification_report(Y_test,predictions))
print(mlp.score(X_test,Y_test))
joblib.dump(mlp,"NN_name.joblib")
