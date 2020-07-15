# Efficiently Planning for Tasks That Involve Tool Construction

This folder contains the core components of tool construction, combined within a task planning framework. This folder is largely self-contained, but for more information on how some of the required csv files were created, please see the pipeline figure in `Tool_Macgyvering`.  

The goal of this work is to enable existing planning algorithms to efficiently plan for tasks that involve tool construction. This can be challenging owing to the combinatorial state space of possible object combinations for tool construction. We compute a visual score that accounts for the shape, material and attachment capabilities of objects, to guide the search for a valid task plan and significantly reduce the computational effort involved. For more details on this work and a description of our algorithm, please refer to our paper on this work: **PAPER**.

## Folder Outline

- `src` folder contains the main components of the algorithm. This code is adapted from **Pyperplan** ([https://github.com/aibasel/pyperplan](https://github.com/aibasel/pyperplan)). The modified components of Pyperplan include `search/astar.py`, `search/enforced_hillclimbing_search.py` and `pyperplan.py`. The new files that are included are `object_score.py` and `planner_interface.py`. 
  - `search/astar.py` and `search/enforced_hillclimbing_search.py` have been modified to include the visual score computation. 
  - `pyperplan.py` has been modified to add supporting functions, and arguments that the user can specify (More details on this in [Run Instructions](#run-instructions)).
  - `object_score.py` reads from csv files that store shape, material and attachment scores for input objects. These scores can be computed using the models in `Tool_Macgyvering/visual_score_prediction` folder. 
  - `planner_interface.py` contains supporting functions for our algorithms, such as functions for tracking the attempted tool constructions and mapping objects in the problem definition to point cloud names. 
  - The `models` folder stores csv files containing shape, material and attachment scores for the 58 point clouds in our dataset. 
  
- `tests` contains PDDL domain and problem definitions for three domains: Assembly, cooking and cleaning. Within each domain, there are two separate tasks that require one tool to be constructed. For example, the problem file `tests/assembly/hit/task01.pddl` requires the construction of a hammer, and the problem file `tests/cooking/flip/task01.pddl` requires the construction of a spatula. The final task plan solution is saved in the corresponding folder with the extension `.pddl.soln`. 
  
- `dataset_cons` contains the testing sets used for our experiments. The folders `hit` and `screw` correspond to the assembly domain; `scoop` and `flip` correspond to the cooking domain; `rake` and `squeegee` correspond to the cleaning domain. There are 10 sets of 10 objects in each domain, created from the dataset of 58 objects. Within each set there is one ground truth construction that the robot has to find within as few attempts as possible. The ground truth construction for each test set is noted in the `Ground_truth.xlsx` file. 

## Code Overview

We start by specifying the problem and domain definitions in PDDL. Note that in the problem definition, the objects are specified as `obj0 obj1 obj2 obj3 obj4 obj5 obj6 obj7 obj8 obj9 - cons-part`. Prior to planning, each object is mapped to a point cloud in one of the test sets in the `dataset_cons` folder. For example, if the specified test set is `dataset_cons/Flip/1`, the objects `obj0` to `obj9` will be mapped to the 10 point clouds in this folder, i.e., `obj0` mapped to `beans_tin.ply` and so on. This is done by the `objectToCloudMap` function in `planner_interface.py`. During planning, the visual score for the objects is computed based on the point clouds that they are mapped to. In our example for `obj0`, the shape, material and attachment scores are retrieved for `beans_tin.ply`. The scores are read from the csv files in the `src/models` folder. Once the scores are retrieved, the visual score is computed by the `scoreCompute` and `attCompute` functions in `planner_interface.py`. The visual score is then incorporated into the heuristic in the `search/astar.py` file. 

## Run Instructions


## Output Descriptions
