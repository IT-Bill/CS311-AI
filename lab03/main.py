from pathlib import Path
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use("TkAgg")
import tomli #the lib to read config file
import sys
from agent import ProblemSolvingAgent
import plotting
from utils.map import mat2obs, read_map


file_folder = Path(__file__).parent # file is more accurate then cwd
test_folder = file_folder/'test_cases'
save_fig =True # whether to generate gif file. If true, the real time display would be much slower. 
image_path = file_folder / 'images'  # image and animation path  
gif_path = file_folder / 'gif'      # gif path
sys.path.append(str(file_folder)) # add the current directory to the path. 

# agent algorithm
agent = ProblemSolvingAgent() # The agent implementation, you should complete the agent.py


case = str(2)
# environment world
with open(test_folder/f'case{case}.toml', 'rb') as f:
    config = tomli.load(f)
world_config = config['world']
map = read_map(world_config, test_folder)
obstacles = mat2obs(map)
# coordinates of origin and destination
start_point = tuple(world_config['start_point'])
goal_point  = tuple(world_config['goal_point'])
# DepthFirstSearch, BreadthFirstSearch, UniformCostSearch(Dijkstra), Greedy BestFirstSearch, Astar
algorithms = ['DFS', 'BFS', 'UCS', 'GBFS', 'Astar']
# for algorithm in algorithms:
# for algorithm in algorithms:
algorithm = 'Astar'
path, visited = agent.solve_by_searching(obstacles, start_point, goal_point, algorithm)
plot = plotting.Plotting(start_point, goal_point, obstacles, 
                        save_fig=save_fig, image_path=image_path, gif_path=gif_path,
                        sampling_period = world_config['sampling_period'])
if save_fig:
    plot.clear_image_path()
plot.animation(path, visited, algorithm)
# plot.generate_gif(algorithm+case, fps=world_config['fps'])
plot.generate_gif(algorithm+case)