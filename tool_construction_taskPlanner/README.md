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
  
- `tests` contains PDDL domain and problem definitions for three domains: Assembly, cooking and cleaning. Within each domain, there are two separate tasks that each require one tool to be constructed. For example, the problem file `tests/assembly/hit/task01.pddl` requires the construction of a hammer, and the problem file `tests/cooking/flip/task01.pddl` requires the construction of a spatula. The final task plan solution is saved in the corresponding folder with the extension `.pddl.soln`. 
  
- `dataset_cons` contains the testing sets of point clouds used for our experiments. The folders `hit` and `screw` correspond to the assembly domain; `scoop` and `flip` correspond to the cooking domain; `rake` and `squeegee` correspond to the cleaning domain. There are 10 sets of 10 objects in each domain, created from the dataset of 58 objects. Within each set there is one ground truth construction that the robot has to find, with as few attempts as possible. The ground truth construction for each test set is noted in the `Ground_truth.xlsx` file. 

## Code Overview

We start by specifying the problem and domain definitions in PDDL. Note that in the problem definition, the objects are specified as `obj0 obj1 obj2 obj3 obj4 obj5 obj6 obj7 obj8 obj9 - cons-part`. Prior to planning, each object is mapped to a point cloud in one of the test sets in the `dataset_cons` folder. For example, if the specified test set is `dataset_cons/Flip/1`, the objects `obj0` to `obj9` will be mapped to the 10 point clouds in this folder, i.e., `obj0` mapped to `beans_tin.ply` and so on. This is done by the `objectToCloudMap` function in `planner_interface.py`. During planning, the visual score for the objects is computed based on the point clouds that they are mapped to. In our example for `obj0`, the shape, material and attachment scores are retrieved for `beans_tin.ply`. These scores are read from the csv files in the `src/models` folder, by the functions in `object_score.py`. Once the scores are retrieved, the visual score is computed by the `scoreCompute` and `attCompute` functions in `planner_interface.py`. The visual score is then incorporated into the heuristic in the `search/astar.py` file. The solution is saved in the same folder as the PDDL problem definition.

## Run Instructions

The following are the relevant user arguments:

- `-s`: Specify the type of search (`astar`, `wastar` or `ehs` for enforced hillclimbing search)
- `-H`: Specify the heuristic to use (`landmark` or `hff`)
- `-vs`: To use visual scoring with heuristic
- `-vso`: To use visual scoring without heuristic
- `-st`: Trust sensors partially (More details on sensor trust is in our paper)
- `-f`: The folder of point clouds that should be used for testing
- `-t`: The folder name for the point clouds (`hit`, `screw`, `scoop`, `rake`, `squeegee` or `flip`)
- Additionally specify the PDDL problem and domain definitions

Example: To run A* search with landmarks heuristic and visual scoring, on folder 1 of hit for assembly tasks, do the following:
`python src\pyperplan.py -s astar -H landmark -vs -f 1 -t hit tests\assembly\domain.pddl tests\assembly\hit\task01.pddl`

To run weighted A* with only visual scoring and no heuristic, on folder 8 of scoop for cooking tasks, do the following:
`python src\pyperplan.py -s wastar -vso -f 8 -t scoop tests\cooking\domain.pddl tests\cooking\scoop\task01.pddl`

To only partially trust the sensors (Specified in conjunction with `-vs` or `-vso` parameters):
`python src\pyperplan.py -s astar -H landmark -vs -st -f 5 -t rake tests\cleaning\domain.pddl tests\cleaning\rake\task01.pddl`

If a plan is found, it will be displayed with the actual names of the point clouds that are used to construct the tool. 
