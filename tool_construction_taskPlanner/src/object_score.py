# Returns shape, material and attachment scores for objects from saved csv files

import csv
import ast
import os
from os.path import join

def shape_score():
    csvname = 'shape.csv'
    cwd = os.getcwd()
    filename = join(cwd, 'src', 'models', csvname)
    shape_dict = {}
    col_dict = {'hit': 1, 'scoop': 2, 'rake': 3, 'screw': 4, 'squeegee': 5, 'flip': 6, 'handle': 7}
    with open(filename) as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            tool_dict = {'hit': 0, 'scoop': 0, 'rake': 0, 'screw': 0, 'squeegee': 0, 'flip': 0, 'handle': 0}
            for tool in tool_dict.keys():
                tool_dict[tool] = ast.literal_eval(row[col_dict[tool]])
            shape_dict[row[0].rstrip()] = tool_dict

        f.close()

    return shape_dict

def mat_score():
    csvname = 'material_class.csv'
    cwd = os.getcwd()
    filename = join(cwd, 'src', 'models', csvname)
    mat_dict = {}
    col_dict = {'hit':1, 'scoop':2, 'rake':3, 'screw':4, 'squeegee':5, 'flip':6}
    with open(filename) as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            tool_dict = {'hit': 0, 'scoop': 0, 'rake': 0, 'screw': 0, 'squeegee': 0, 'flip': 0}
            for tool in tool_dict.keys():
                if row[col_dict[tool]] == 'inf':
                    tool_dict[tool] = -float('inf')
                else:
                    tool_dict[tool] = ast.literal_eval(row[col_dict[tool]])
            mat_dict[row[0].rstrip()] = tool_dict

        f.close()

    return mat_dict

def att_score(att_type):
    if att_type == 'pierce':
        csvname = 'pierce.csv'
        cwd = os.getcwd()
        filename = join(cwd, 'src', 'models', csvname)
        return pierce(filename)
    elif att_type == 'grasp':
        csvname = 'grasp.csv'
        cwd = os.getcwd()
        filename = join(cwd, 'src', 'models', csvname)
        return grasp(filename)
    elif att_type == 'magnetic':
        csvname = 'magnets.csv'
        cwd = os.getcwd()
        filename = join(cwd, 'src', 'models', csvname)
        return magnetic(filename)
    else:
        raise ValueError("Incorrect attachment type \n")

def pierce(filename=None):
    pierce_vals = {}
    with open(filename) as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            pierce_vals[row[0].rstrip()] = True if ast.literal_eval(row[1]) > 0 else False

    f.close()

    return pierce_vals

def grasp(filename=None):
    grasp_vals = {}
    with open(filename) as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            grasp_vals[row[0].rstrip()] = True if ast.literal_eval(row[1]) > 0 else False

    f.close()

    return grasp_vals

def magnetic(filename=None):
    mag_vals = {}
    with open(filename) as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            mag_vals[row[0].rstrip()] = True if ast.literal_eval(row[1]) > 0 else False

    f.close()

    return mag_vals

'''ply = 'wood_spread_tooth.ply'
reference_action = 'rake'

print(shape_score(ply, reference_action))
print(mat_score(ply, reference_action))

att_type = 'pierce'
print(att_score(ply, att_type))
att_type = 'grasp'
print(att_score(ply, att_type))
att_type = 'magnetic'
print(att_score(ply, att_type))'''
