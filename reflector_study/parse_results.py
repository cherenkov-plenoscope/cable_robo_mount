import json
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import *

directory = 'C:\\Users\\Spiros Daglas\\Desktop\\run\\dish50_BFangle045_tr18_xoz12_fct06_cablescs_bartr_barr_CARBON65'

def results_for_case(directory):
    particles = dirs = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    directories = list(map(int, particles))
    directories.sort(key=int)
    return directories

def collect_data(directory, file_name, dict_key):
    directories = results_for_case(directory)
    dict_data = []
    for dir_number in directories:
        json_path = os.path.join(directory, str(dir_number), file_name)
        try:
            with open(json_path) as json_data:
                json_dictionary = json.load(json_data)
                dict_data.append(json_dictionary[dict_key])
        except:
            pass
    return np.array(dict_data)

def create_history_of_data(directory=directory, file_name='intermediate_results.json', dict_key='reflector_weight'):
    dict_data=collect_data(directory, file_name, dict_key)
    min_dict_data=dict_data.min()
    iter_number_of_min_dict_data = np.argmin(dict_data)
    plt.bar(left=np.arange(len(dict_data)), height=dict_data, width=1.0, color='green')
    plt.xlabel('Iteration count')
    plt.ylabel(str(dict_key))
    plt.title('Progress of PSO. Best iteration:'+str(iter_number_of_min_dict_data)+' with '+dict_key+': '+str(min_dict_data))
    plt.xlim(xmin=0)
    plt.grid(True)

    plt.show()
    return dict_data

def collect_pareto_points(directory=directory, file_name='variables_vector.json'):
    json_path = os.path.join(directory, str(0), file_name)
    try:
        with open(json_path) as json_data:
            json_list = json.load(json_data)
            variables_number = len(json_list)
    except:
        pass
    pareto_points = []
    for i in range(variables_number):
        pareto_points.append(collect_data(directory=directory, file_name=file_name, dict_key=i).tolist())
    return np.transpose(np.array(pareto_points))

def simple_cull(pts, dominates):
    dominated = []
    cleared = []
    remaining = pts
    while remaining:
        candidate = remaining[0]
        new_remaining = []
        for other in remaining[1:]:
            [new_remaining, dominated][dominates(candidate, other)].append(other)
        if not any(dominates(other, candidate) for other in new_remaining):
            cleared.append(candidate)
        else:
            dominated.append(candidate)
        remaining = new_remaining
    return cleared, dominated

def dominates(row, rowCandidate):
    return all(r <= rc for r, rc in zip(row, rowCandidate))

#inputPoints = collect_pareto_points(directory)[:,:3].tolist()
#paretoPoints, dominatedPoints = simple_cull(inputPoints, dominates)

def plot_pareto_surface(paretoPoints, dominatedPoints):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    plt.hold(True)

    dp = np.array(list(dominatedPoints))
    pp = np.array(list(paretoPoints))
    print(pp.shape,dp.shape)
    ax.grid(True)
    ax.set_title("Pareto front")
    ax.scatter(dp[:,0],dp[:,1],dp[:,2], color= "r")
    ax.scatter(pp[:,0], pp[:,1], pp[:,2], color= "b")
    ax.plot_trisurf(pp[:,0], pp[:,1], pp[:,2], cmap= "viridis")
    """
    X,Y,Z = np.meshgrid(pp[:,0], pp[:,1], pp[:,2])
    ax.contour(X, Y, Z, zdir='y', offset= -1, cmap="autumn")
    """
    plt.show()

def make_bar_graph_from_array(array):
    plt.bar(left=np.arange(len(array)), height=array, width=1.0, color='green')
    plt.show()
