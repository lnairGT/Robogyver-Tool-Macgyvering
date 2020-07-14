# Planner interface
# This code i) retrieves shape, material and attachment information for objects (setShapeScore, setMatScore, setAtt)
#          ii) maps object point clouds to objects in the PDDL problem definition (objToCloudMap)
#         iii) Parses the PDDL actions, objects and solutions (object/action/solutionParser)
#          iv) Checks whether the planner found the ground truth construction (objValidate)
#           v) Compute shape/material score and check if attachments exist (scoreCompute, AttCompute)
#          vi) Store information from user input arguments into flags (setFlags)
# NOTE: objectParser also tracks the object combinations that have been attempted so far

import os
from os import listdir
from os.path import isfile, join
from object_score import *
import ast

# Make object map and flags accessible to all functions
global pcl_object_map
pcl_object_map = {}

global object_combinations
object_combinations = []

global settings_flag
settings_flag = {}

# Store shape and material scores
global shape_score_dict
shape_score_dict = {}

global mat_score_dict
mat_score_dict = {}

# Store attachments
global pierce_dict
pierce_dict = {}

global grasp_dict
grasp_dict = {}

global magnet_dict
magnet_dict = {}

def setFlags(arg_visual, no_ff, arg_trust):
    # Keeps track of the input argument corresponding to the method
    if arg_visual:
        # Use visual scoring with FF for -vs argument
        settings_flag['vs_flag'] = True
        settings_flag['ff_flag'] = True
    else:
        # Not using visual scoring
        settings_flag['vs_flag'] = False
        settings_flag['ff_flag'] = True

    if no_ff:
        # Automatically use visual scoring without FF for -vso argument
        settings_flag['vs_flag'] = True
        settings_flag['ff_flag'] = False

    if arg_trust:
        # Don't trust sensor completely if -st is set as argument
        settings_flag['trust'] = True
    else:
        settings_flag['trust'] = False

    return settings_flag

def setShapeScore():
    temp = shape_score()
    for key in temp.keys():
        shape_score_dict[key] = temp[key]
    return shape_score_dict

def setMatScore():
    temp = mat_score()
    for key in temp.keys():
        mat_score_dict[key] = temp[key]
    return mat_score_dict

def setAtt():
    temp_pierce = att_score('pierce')
    temp_grasp = att_score('grasp')
    temp_mag = att_score('magnetic')

    for key in temp_pierce.keys():
        pierce_dict[key] = temp_pierce[key]
        grasp_dict[key] = temp_grasp[key]
        magnet_dict[key] = temp_mag[key]

    return pierce_dict, grasp_dict, magnet_dict

def objToCloudMap(tool_type, folder_num):

    # Create object map
    folder_name = join(os.getcwd(), 'dataset_cons', tool_type, folder_num)
    cloud_list = [f for f in listdir(folder_name) if isfile(join(folder_name, f))]

    for idx, cloud in enumerate(cloud_list):
        pcl_object_map['obj'+str(idx)] = cloud

    return pcl_object_map

def scoreCompute(action_part, handle_part, tool_type, shapeOnly=False):
    # Start by eliminating parts based on material fitness, then moving onto shape score

    # Material score computation
    score_mat = mat_score_dict[action_part][tool_type]

    if not score_mat:
        raise ValueError("Material for action part %s not found" % (action_part))
    elif score_mat == -float('inf') and not shapeOnly:
        # No need to compute shape score if material score is infinity
        return score_mat

    # Weight material and shape scores
    geo_wt = 1.0
    mat_wt = 1.0

    # Shape score computation
    score_action = shape_score_dict[action_part][tool_type]
    score_handle = shape_score_dict[handle_part]['handle']

    if not score_action:
        raise ValueError("Action part %s not found" % (action_part))
    if not score_handle:
        raise ValueError("Handle part %s not found" % (handle_part))

    if shapeOnly:
        # Only compute shape score
        return geo_wt * score_action * score_handle

    return (geo_wt * score_action * score_handle) + (mat_wt * score_mat)

def attCompute(action_part, handle_part):
    # Check if parts can be attached

    # If attachments disabled, just return True
    if not pierce_dict or not grasp_dict or not magnet_dict:
        return True

    # Otherwise check if attachments are possible
    if 'screwdriver' in handle_part:
        return pierce_dict[action_part]
    elif 'pliers' in handle_part or 'tongs' in handle_part:
        return grasp_dict[action_part]
    else:
        return magnet_dict[action_part] and magnet_dict[handle_part]

def objectParser(solution):
    for step in solution:
        if 'join-' in step.name:
            action_part, handle_part, _ = actionParser(step)
            if (action_part, handle_part) not in object_combinations:
                object_combinations.append((action_part, handle_part))
            break

    return object_combinations

def actionParser(op):
    assert 'join-' in op.name
    a, action_part, handle_part = op.name.split()
    tool_type = a[6:] # Name of tool from action

    # Remove last character from handle name
    handle_part = handle_part[0:-1]

    # Find object in pcl_object_map
    action_part = pcl_object_map[action_part]
    handle_part = pcl_object_map[handle_part]

    return action_part, handle_part, tool_type

def solutionParser(solution, obj_map):
    updated_solution = []

    for step in solution:
        step_name = str(step.name)

        for key in obj_map.keys():
            if key in step_name:
                step_name = step_name.replace(key, obj_map[key])

        updated_solution.append(step_name)

    return updated_solution

def objValidate(solution, ground_truth):
    for step in solution:
        if 'join-' in step.name:
            action_part, handle_part, _ = actionParser(step)

            if (ground_truth[0] not in action_part) or (ground_truth[1] not in handle_part):
                return False
            else:
                return True