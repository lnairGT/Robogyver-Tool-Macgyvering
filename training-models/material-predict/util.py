import glob, csv, os
import numpy as np
import cPickle as pickle

def loadScioDataset(pklFile='sciodata', csvFile='scio_allmaterials_clean', materialNames=[], objectNames=[]):
    saveFilename = os.path.join('data', pklFile + '.pkl')
    if os.path.isfile(saveFilename):
        with open(saveFilename, 'rb') as f:
            X, y_materials, y_objects, wavelengths = pickle.load(f)
    else:
        X = []
        y_materials = []
        y_objects = []
        filename = os.path.join('data', csvFile + '.csv')
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
                if obj not in objectNames[index]:
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


