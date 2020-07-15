# Efficiently Planning for Tasks That Involve Tool Construction

This folder contains the core components of tool construction, combined within a task planning framework. This folder is largely self-contained, but for more information on how some of the required csv files were created, please see the pipeline figure in `Tool_Macgyvering`.  

The goal of this work is to enable existing planning algorithms to efficiently plan for tasks that involve tool construction. This can be challenging owing to the combinatorial state space of possible object combinations for tool construction. We compute a visual score that accounts for the shape, material and attachment capabilities of objects, to guide the search for a valid task plan and significantly reduce the computational effort involved. For more details on this work and a description of our algorithm, please refer to our paper on this work: **PAPER**.

## Folder Outline

- `src` folder contains the main components of the algorithm. This code is adapted from **Pyperplan** ([https://github.com/aibasel/pyperplan](https://github.com/aibasel/pyperplan)). The modified components of Pyperplan include `search/astar.py`, `search/enforced_hillclimbing_search.py` and `pyperplan.py`. The new files that are included are `object_score.py` and `planner_interface.py`. 
  - `search/astar.py` and `search/enforced_hillclimbing_search.py` have been modified to include the visual score computation. 
  - `pyperplan.py` has been modified to add supporting functions, and arguments that the user can specify (More details on this in [Run Instructions](#run-instructions)).

## Code Specifics


## Run Instructions


## Output Descriptions
