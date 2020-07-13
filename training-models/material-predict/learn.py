import os, sys
import numpy as np
import cPickle as pickle

from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, LeakyReLU
from keras.optimizers import Adam
from keras.utils.np_utils import to_categorical

from sklearn.preprocessing import Normalizer, StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold

import util

scale = 'scaler'
classifier = 'nn'
predictPiercability = True


materials = ['plastic', 'fabric', 'paper', 'wood', 'metal', 'foam']

plastics = ['HDPE', 'PET', 'polyethyleneBlue', 'polyethyleneGreen', 'polyethyleneRed', 'polyethyleneYellow', 'PP', 'PVC', 'thermoPolypropylene', 'thermoTeflon']
fabrics = ['cottonCanvas', 'cottonSweater', 'cottonTowel', 'denim', 'felt', 'flannel', 'gauze', 'linen', 'satin', 'wool']
papers = ['cardboard', 'constructionPaperGreen', 'constructionPaperOrange', 'constructionPaperRed', 'magazinePaper', 'newspaper', 'notebookPaper', 'printerPaper', 'receiptPaper', 'textbookPaper']
woods = ['ash', 'cherry', 'curlyMaple', 'hardMaple', 'hickory', 'redCedar', 'redElm', 'redOak', 'walnut', 'whiteOak']
metals = ['aluminum', 'aluminumFoil', 'brass', 'copper', 'iron', 'lead', 'magnesium', 'steel', 'titanium', 'zinc']
objects = [plastics, fabrics, papers, woods, metals]

foam = ['styrofoam_cup', 'ball', 'pie', 'dinosaur_yellow', 'dinosaur_blue', 'dinosaur_purple', 'dinosaur_green', 'dinosaur_orange', 'toad_mario', 'baseball', 'white_sheets', 'black_sheets', 'styrofoam_block', 'sandal']
objects2 = [[], [], [], [], [], foam]

saveFilename = os.path.join('data', 'smm50_scio.pkl')
with open(saveFilename, 'rb') as f:
    X, y_materials, y_objects, wavelengths = pickle.load(f)

X2, y_materials2, y_objects2, _ = util.loadScioDataset(pklFile='scio_everyday_objects_expanded', csvFile='scio_everyday_objects_expanded', materialNames=materials, objectNames=objects2)
print np.shape(X), np.shape(y_materials), np.shape(y_objects), np.shape(X2), np.shape(y_materials2), np.shape(y_objects2)

X = np.concatenate([X, X2], axis=0)
y_materials = np.concatenate([y_materials, y_materials2], axis=0)
y_objects = np.concatenate([y_objects, y_objects2], axis=0)
wavelengths = np.array(wavelengths)
print np.shape(X), np.shape(y_materials), np.shape(y_objects), np.shape(X2), np.shape(y_materials2), np.shape(y_objects2)

# Use only 10 samples from each object
samples = 10
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
print np.shape(X), np.shape(y_materials), np.shape(y_objects)

X = util.firstDeriv(X, wavelengths)
y = np.array(y_materials)

if predictPiercability:
    # Switch from predicting materials to predicting piercability of an object (binary output)
    y_new = []
    for ym, yo in zip(y_materials, y_objects):
        y_new.append(1 if materials[ym] == 'foam' and yo not in ['toad_mario', 'baseball', 'sandal'] else 0)
    y = np.array(y_new)

skf = StratifiedKFold(n_splits=len(materials), shuffle=True, random_state=0)

accuracies = []
for iteration, (train_index, test_index) in enumerate(skf.split(X, y)):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]

    if scale is not None:
        scaler = StandardScaler() if scale == 'scale' else Normalizer()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)
        # print np.min(X_train), np.max(X_train)
        # print np.min(X_test), np.max(X_test)

    if classifier == 'svm':
        model = SVC(C=1, kernel='rbf')
        model.fit(X_train, y_train)
        accuracies.append(model.score(X_test, y_test))
    elif classifier == 'nn':
        num_classes = len(set(y))
        y_train = to_categorical(y_train, num_classes)
        y_test = to_categorical(y_test, num_classes)

        model = Sequential()
        model.add(Dense(256, activation='relu', input_shape=(np.shape(X_train)[-1],)))
        # model.add(Dropout(0.2))
        model.add(Dense(256, activation='relu'))
        # model.add(Dropout(0.2))
        model.add(Dense(num_classes, activation='softmax'))

        # d = [64]*2 + [32]*2
        # model = Sequential()
        # model.add(Dense(d[0], activation='linear', input_dim=np.shape(X)[-1]))
        # # model.add(Dropout(0.05))
        # model.add(Dropout(0.25))
        # model.add(LeakyReLU())
        # for dd in d[1:]:
        #     model.add(Dense(dd, activation='linear'))
        #     # model.add(Dropout(0.05))
        #     model.add(Dropout(0.25))
        #     model.add(LeakyReLU())
        # model.add(Dense(materialCount, activation='softmax'))
        # model.compile(loss='categorical_crossentropy', optimizer=Adam(lr=0.0005), metrics=['accuracy'])

        # Adam(lr=0.0001)
        model.compile(loss='categorical_crossentropy' if not predictPiercability else 'binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        model.fit(X_train, y_train, batch_size=16, epochs=20, verbose=1, validation_data=(X_test, y_test))

        loss, accuracy = model.evaluate(X_test, y_test, verbose=1)
        accuracies.append(accuracy)

    print 'Iteration %d. Test accuracy:' % iteration, accuracies[-1]

print 'All accuracies:', accuracies
print 'Average accuracies:', np.mean(accuracies)




