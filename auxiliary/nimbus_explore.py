import csv
import ast
import os.path
import random
import copy

from object_class import MG_object
from pierce_predict import *
from sklearn.externals import joblib

# --------- FILE/DATA READING RELATED FUNCTIONS ---------- #
def object_pose_reader(object_pose_file):
	# Read the point cloud poses of objects, transform it into real-world coordinates
	# {obj_name: geometry_msg_Pose}
	obj_poses = {}

	with open(object_pose_file) as f:
		reader = csv.reader(f)
		obj_pose = geometry_msgs.msg.Pose()
		for row in reader:
			obj_pose.position.x = row[1]
			obj_pose.position.y = row[2]
			obj_pose.position.z = row[3]
			obj_poses[row[0]] = obj_pose

	return obj_poses

def ESF_retrieve(point_cloud, esf_file=None): # CHECK THIS ONE
	ESF = {}
		if esf_file is None:
		ESF_file = 'esf_descriptors_final_DS.csv' # Specify new ESF file
	else:
		ESF_file = esf_file

	with open(ESF_file) as f:
		reader = csv.reader(f)
		reader.next()
		for idx, row in enumerate(reader):
			if row[0] == point_cloud:
				ESF_features = [ast.literal_eval(row[i+1]) for i in range(0,640)]
				return ESF_features

	return None

def add_substitutes(objects_attr, object_rank, objects_list):
	# Add the single objects to object_rank, with geoscore from pierce predict, material of zero, att type of 'subs' and att score of 0.
	idx = len(object_rank)

	for obj in objects_list:
		object_rank.append(((obj), idx))
		objects_attr[((obj), idx)] = {'geoscore':0, 'att_type':'subs', 'att_score':0, 'material_score':0, 'total_score':0}
		idx = idx + 1

	return objects_attr, object_rank

def geoscore_predict(obj_1, obj_2, reference_action, learning_file):
	action_part = ESF_retrieve(obj_1)
	grasp_part = ESF_retrieve(obj_2)

	if action_part == None or grasp_part == None:
		print("ERROR: ESF features not found")

	joblib_location = '' #Location of joblib file for predicting shape score

	if reference_action == 'seven':
		model_action = joblib.load(joblib_location + learning_file)
		tool_types = ['contain', 'cut', 'flip', 'hit', 'poke', 'scoop']
		reference_idx = tool_types.index(reference_action)
		score = model_action.predict_proba(np.array(action_part).reshape(1, -1))
		action_score = score[0][reference_idx]
		grasp_score = score[0][6] # handle

	else:
		model_action = joblib.load(joblib_location + learning_file)
		model_grasp = joblib.load(joblib_location + 'ESF_NN_Handles_Final.joblib')
		
		a_score = model_action.predict_proba(np.array(action_part).reshape(1, -1))
		action_score = a_score[0][1]
		
		g_score = model_grasp.predict_proba(np.array(grasp_part).reshape(1, -1))
		grasp_score = g_score[0][1]
	
	geoscore = action_score * grasp_score

	return geoscore

def output_reader(output_file, reference_action=None, learning_file=None, arbitration_type=None):
	object_rank = []
	objects_attr = {}
	objects_list = []

	with open(output_file) as f:
		reader = csv.reader(f)
		reader.next() # Skip header
		for idx, row in enumerate(reader):
			obj_1 = row[0]
			obj_2 = row[1]
			att_type = row[2]

			if learning_file is None:
				geo_score = ast.literal_eval(row[3])
			else:
				geo_score = geoscore_predict(obj_1, obj_2, reference_action, learning_file)

			att_score = ast.literal_eval(row[4]) if row[4] != 'Inf' else float(row[4])
			object_rank.append(((obj_1, obj_2), idx))
			objects_attr[((obj_1, obj_2), idx)] = {'geoscore': geo_score, 'att_type': att_type, 'att_score':att_score, 'material_score':0, 'total_score':geo_score}

			if obj_1 not in objects_list:
				objects_list.append(obj_1) # List of available objects

	if arbitration_type is not None:
		objects_attr, object_rank = add_substitutes(object_rank, objects_list)
		objects_attr = arbitration(objects_attr, reference_action, arbitration_type)

	return object_rank, objects_attr, objects_list

def rank2csv(obj_rank, obj_attr, final_file_loc = None):
	data = {}
	final_dict = {}
	field_names = ['obj_combo', 'geoscore', 'att_type', 'att_score', 'material_score', 'total_score']

	if final_file_loc is None:
		final_rank_file = 'final_rank.csv'
	else:
		final_rank_file = os.path.join(final_file_loc, 'final_rank.csv')

	print final_rank_file

	with open(final_rank_file, 'w') as f:
		writer = csv.DictWriter(f, fieldnames = field_names)
		writer.writeheader()
		for elt in obj_rank:
			final_dict = obj_attr[elt[0]]
			data['obj_combo'] = elt[0][0] #[0]
			final_dict.update(data)
			writer.writerow(final_dict)

# --------- OBJECT SCORING/RANKING RELATED FUNCTIONS ----- #

def top_rank_select():
	# Function that returns N top ranked objects from an input list of combos
	pass

def object_reranking(objects_attr, MG_objs_list, att_types_used, dual_NN_embeddings=None, dual_NN_wts=None, dual_NN_scaler=None, normalize=False, user_rank=None, arbitration_type=None):
	# Adds attachment scores to current ranking scores and re-ranks them
	# Add material properties scores
	objects_attr_new = objects_attr.copy()
	total_scores = []
	new_rank = []

	pierce_penalty = 0.0 #0.55  # penalty to impose over pierce attachment since it deforms the object
	magnetic_wt = 1.0 # weighting associated with magnetic attachment
	grasp_wt = 1.0 # weighting associated with grasp attachment
	materials_wt = 1.0 #1.0 #1.0 #1.0 # weighting associated with materials match

	materials_score = [0.0, 0.25, 0.5, 1.0]

	att_wt = 1.0 #0.0 # to rank based on attachment score only

	# Normalize attachment score to between 0 and 1
	# - scale factor is max of attachment scores in a given ranking
	if normalize:
		att_score_list = []
		for pairs in objects_attr_new:
			mg_obj_1 = MG_objs_list[pairs[0][0]]
			if mg_obj_1.pierce_predict == 1:
				att_score_list.append(objects_attr_new[pairs]['att_score'])
		scaling_factor = -max(att_score_list)
	else:
		scaling_factor = -1.0

	for pairs in objects_attr_new:
		if 'pierce' in objects_attr_new[pairs]['att_type'] and 'pierce' in att_types_used:
			mg_obj_1 = MG_objs_list[pairs[0][0]]
			if mg_obj_1.pierce_predict == 0:
				objects_attr_new[pairs]['total_score'] = -float('inf') # Not pierceable
			elif mg_obj_1.pierce_predict == 1:
				objects_attr_new[pairs]['total_score'] = att_wt * objects_attr_new[pairs]['total_score'] + (objects_attr_new[pairs]['att_score']/scaling_factor) + pierce_penalty
			else:
				print("When ranking, object pierceability Unknown encountered")
				objects_attr_new[pairs]['total_score'] = -float('inf')

		elif 'grasp' in objects_attr_new[pairs]['att_type'] and 'grasp' in att_types_used:
			objects_attr_new[pairs]['total_score'] = att_wt * objects_attr_new[pairs]['total_score'] + grasp_wt * (objects_attr_new[pairs]['att_score']/scaling_factor)

		elif 'magnetic' in objects_attr_new[pairs]['att_type'] and 'magnetic' in att_types_used:
			objects_attr_new[pairs]['total_score'] = att_wt * objects_attr_new[pairs]['total_score'] + magnetic_wt * (objects_attr_new[pairs]['att_score']/scaling_factor)

		elif 'None' in objects_attr_new[pairs]['att_type']:
			objects_attr_new[pairs]['total_score'] = -float('inf') # No attachments possible

		elif 'subs' in objects_attr_new[pairs]['att_type']:
			objects_attr_new[pairs]['total_score'] = 0 # Substitutes have no attachment score

		if dual_NN_embeddings is not None: ## Use Dual NN
			obj_name = pairs[0][0]
			scio_features = object_sense(obj_name)

			trained_embeddings_folder = '' # Location of embeddings
			trained_wts_folder = '' # Location of model weights
			trained_scaler_folder = '' # Location of scalar weights

			mat_score = materials_dualNN(scio_features, trained_embeddings_folder + dual_NN_embeddings, trained_wts_folder + dual_NN_wts, trained_scaler_folder + dual_NN_scaler)
			if mat_score <= 0.5:  # Probability less than 50% then automatically infinity
				mat_score = -float('inf')

			objects_attr_new[pairs]['material_score'] = mat_score
			objects_attr_new[pairs]['total_score'] = att_wt * objects_attr_new[pairs]['total_score'] + materials_wt * objects_attr_new[pairs]['material_score']

		if arbitration_type == 'rule':
			reference_action = None
			objects_attr_new = arbitration(objects_attr_new, reference_action, arbitration_type)

		total_scores.append((pairs, objects_attr_new[pairs]['total_score']))

	# Sort based on total_score
	total_scores.sort(key=lambda x: x[1], reverse=True)
	for idx, item in enumerate(total_scores):
		new_rank.append((item[0], idx+1))

	return new_rank, objects_attr_new

def update_attr(obj_attr, obj_poses, key, reference_action):
	# Update predicted attributes of objects
	if key in obj_poses.keys():
		mg_obj = MG_object(key, obj_poses[key])
	else:
		mg_obj = MG_object(key, None)

	for pairs in obj_attr.keys():
		# If first object is graspable by tool
		if key in pairs[0][0] and 'grasp' in obj_attr[pairs]['att_type']:
			mg_obj.set_attribute('grasp_predict', 1)

	if mg_obj.grasp_predict is None:
		mg_obj.set_attribute('grasp_predict', 0)    # Since this was not set to 1, it has to be 0

	if mg_obj.pierce_predict is None:
		# Move sensor over object and sense pierceability and material class
		#scio_features = np.array([object_sense(key, obj_poses[key])])
		scio_features = object_sense(key, mg_obj.obj_position)
		pierce_value = pierce_predict(scio_features, pierce_classifier[0], pierce_classifier[1])
		mg_obj.set_attribute('pierce_predict', pierce_value)

		if mg_obj.material_class is None:
			material_class = materials_predict(scio_features, materials_classifier[0], materials_classifier[1])
			mg_obj.set_attribute('material_class', material_class[0])

	return mg_obj

# ---------- ATTACH, GRASP RELATED FUNCTIONS ------------- #

def object_test(test_name, object_pose):
	# Move to location specified by object_pose and perform test corresponding to test_name
	pass

# ---------- SCIO SENSING FUNCTIONS ---------------------- #

def object_sense(obj_name, obj_pose=None):
	MG_dataset = 'SCiO_finalDS_unprocessed.csv'

	scio_features = features_scio(MG_dataset)

	if obj_name not in scio_features.keys():
		print "Object not found: %s" %(obj_name)
		return None
	else:
		return scio_features[obj_name]

def user_input(s):
	user_in = raw_input(s)
	if 'y' in user_in.lower():
		return True
	else:
		return False


## Iterate over the folders:

main_folder_loc = '' # Folders with test cases for tool construction
tool_folders = ['Flip', 'Hit', 'Rake', 'Scoop', 'Screw', 'Squeegee'] #['Flip', 'Hit', 'Rake', 'Scoop', 'Screw', 'Squeegee'] # FLIP
num_sub_cases = 10

for tool_folder in tool_folders:
	for folder_num in range(0,num_sub_cases):
		output_file_loc = os.path.join(main_folder_loc, tool_folder, str(folder_num+1))
		output_file = os.path.join(output_file_loc, 'output_rankings.csv')

		# Main function

		time_start = time.time()

		#rospy.init_node('nimbus_explore')

		poses_file = 'Object_positions.csv'
		pierce_classifier = ['pierce_NN.json', 'pierce_wts.h5']
		materials_classifier = ['materials_NN.json', 'materials_wts.h5']
		user_rank = None
		construct_tool = False # Flag on whether to proceed with actual tool construction
		normalize = False
		dual_NN_flag = True # Use Dual NN for material reasoning

		# RSS parameters
		method = 'RSS' # or ICRA

		if method == 'RSS':
			reference_action = tool_folder.lower() #'flip' # or seven
			seven_class = False # Seven-class model or not

			if reference_action == 'hit':
				learning_file = 'ESF_NN_Hammer_Final.joblib'	
				user_rank = ['wood', 'metal']
			elif reference_action == 'scoop':
				learning_file = 'ESF_NN_Scoop_Contain.joblib'
				user_rank = ['wood', 'metal', 'plastic']
			elif reference_action == 'squeegee':
				learning_file = 'ESF_NN_Squeegee_Final.joblib'
				user_rank = ['foam']
			elif reference_action == 'flip':
				learning_file = 'ESF_NN_Spatula_Final.joblib'
				user_rank = ['metal', 'wood', 'plastic']
			elif reference_action == 'screw':
				user_rank = ['metal', 'plastic']
				learning_file = 'ESF_NN_Screwdriver_Final.joblib'
			elif reference_action == 'rake': 
				user_rank = ['metal', 'wood', 'plastic']
				learning_file = 'ESF_NN_Rake_Final.joblib'
			else:
				print "Unknown reference action specified \n"

			if seven_class:
				# This is the 7-class NN
				print "This is a 7-class prediction model \n"
				learning_file = 'NN_ESF.joblib'

			att_types_used = ['pierce', 'grasp', 'magnetic']

			if dual_NN_flag:
				user_rank = None
				dual_NN_embeddings = 'embeddings_material_prop_' + reference_action + '.npy'
				dual_NN_wts = 'material_prop_weights_' + reference_action + '.h5'
				dual_NN_scaler = 'scaler_materials_' + reference_action + '.save'
			else:
				dual_NN_embeddings = None
				dual_NN_wts = None
				dual_NN_scaler = None

		elif method == 'ICRA':
			reference_action = None
			learning_file = None
			att_types_used = ['magnetic']

		obj_rank, obj_attr, obj_list = output_reader(output_file, reference_action, learning_file)
		obj_poses = object_pose_reader(poses_file)

		MG_objs_list = {}
E
		for key in obj_list:   
			MG_objs_list[key] = update_attr(obj_attr, obj_poses, key, reference_action)

		# RANDOM RANKING
		#new_obj_rank = copy.copy(obj_rank)
		#random.shuffle(new_obj_rank)
		#rank2csv(new_obj_rank, obj_attr, output_file_loc)	    

		# Re-rank objects 
		new_obj_rank, obj_attr_new = object_reranking(obj_attr, MG_objs_list, att_types_used, dual_NN_embeddings, dual_NN_wts, dual_NN_scaler, normalize, user_rank)
		rank2csv(new_obj_rank, obj_attr_new, output_file_loc)

		time_elapsed = time.time() - time_start
		print "The reference action is: %s" %(reference_action)
		print "The total time elapsed is: %s" %(time_elapsed)
		print "The total size of the computation space is: %s" %(len(obj_rank))

		# Physical tool construction
		if construct_tool:
			# Flag indicating whether working tool found
			working_tool = False

			while not working_tool:
				pairs = [i[0] for i in new_obj_rank]
				for pair in pairs:
					object_1 = pair[0][0]
					object_2 = pair[0][1]
					att_type = obj_attr_new[pair]['att_type']

					if object_1 in MG_objs_list.keys():
						mg_obj = MG_objs_list[object_1]
					else:
						print "Couldn't find actual object in list of MG objects \n"

					attach_fail_flag = False

					# Perform sequence of move, pick etc. actions to attach the parts

					#################################################################

					if 'None' in att_type: # No attachments, move to next construction
						continue

					att_outcome = user_input('Is attachment successful? ')
					# Modify actual attachment attributes based on user input
					if 'grasp' in att_type:
						if att_outcome:
							mg_obj.set_attribute('grasp_actual', 1)
						else:
							print "Object grasp at specified location failed \n"
							mg_obj.set_attribute('grasp_actual', 0)
							obj_attr_new[pair]['total_score'] = -float('inf')
							attach_fail_flag = True
					elif 'pierce' in att_type:
						if att_outcome:
							mg_obj.set_attribute('pierce_actual', 1)
						else:
							print "Object pierce at specfied location failed \n"
							mg_obj.set_attribute('pierce_actual', 0)
							obj_attr_new[pair]['total_score'] = -float('inf')
							attach_fail_flag = True
					elif 'magnetic' in att_type:
						if not att_outcome:
							print "Object magnetic attachment at specified location failed \n"
							obj_attr_new[pair]['total_score'] = -float('inf')
							attach_fail_flag = True

					if attach_fail_flag:
						# Construction failed, need to re-rank before next construction
						print "Tool construction failed \n"
						break
					else:
						print "Tool construction complete. Testing the constructed tool \n"
						# If attachment succeeded, perform tool testing and get user input on if tool succeeded
						# TEST TOOL

						####################################################################

						working_tool = user_input('Did tool succeed? ')
						if working_tool:
							print "Testing successful! Tool found! \n"
							print "Tool combination: "
							print "Action Part: %s" %(object_1)
							print "Grasp Part: %s \n" %(object_2)
							break  # Working construction found -- STOP
						else:
							print "Testing unsuccessful. Attempting next construction. \n"

				if attach_fail_flag:
					# Rerank only if an attachment in real-world failed
					new_obj_rank, obj_attr_new = object_reranking(obj_attr_new, MG_objs_list, att_types_used, learning, user_rank)

			rank2csv(new_obj_rank, obj_attr_new)