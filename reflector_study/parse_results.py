import json
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import *

directory = 'C:\\Users\\Spiros Daglas\\Desktop\\run\\dish50_3L_fitness_carbon'

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

def save_int_res():
    create_history_of_data(directory=directory, file_name='intermediate_results.json', dict_key='stddev_of_psf')
    create_history_of_data(directory=directory, file_name='intermediate_results.json', dict_key='max_final_deformation')
    create_history_of_data(directory=directory, file_name='intermediate_results.json', dict_key='max_intial_deformation')
    create_history_of_data(directory=directory, file_name='intermediate_results.json', dict_key='max_in_plane_final_deformation')
    create_history_of_data(directory=directory, file_name='intermediate_results.json', dict_key='reflector_weight')
    create_history_of_data(directory=directory, file_name='intermediate_results.json', dict_key='tension_ring_weight')


def create_fitness_history_of_data():
    fitness_function = collect_data(directory=directory, file_name='intermediate_results.json', dict_key='fitness_function')
    stddev_of_psf = collect_data(directory=directory, file_name='intermediate_results.json', dict_key='stddev_of_psf') / 1
    reflector_weight = collect_data(directory=directory, file_name='intermediate_results.json', dict_key='reflector_weight') / 450
    tension_ring_weight = collect_data(directory=directory, file_name='intermediate_results.json', dict_key='tension_ring_weight') / 187
    max_final_deformation = collect_data(directory=directory, file_name='intermediate_results.json', dict_key='max_final_deformation') / 0.6
    plt.ion()
    g1=plt.plot(np.arange(len(fitness_function)), fitness_function, color="black", linewidth= 2.0)[0]
    g2=plt.plot(np.arange(len(stddev_of_psf)), stddev_of_psf, color= "r")[0]
    g3=plt.plot(np.arange(len(reflector_weight)), reflector_weight, color= "b")[0]
    g4=plt.plot(np.arange(len(tension_ring_weight)), tension_ring_weight, color= "g")[0]
    g5=plt.plot(np.arange(len(max_final_deformation)), max_final_deformation, color= "m")[0]
    ax = plt.gca()

    while True:
        fitness_function = collect_data(directory=directory, file_name='intermediate_results.json', dict_key='fitness_function')
        stddev_of_psf = collect_data(directory=directory, file_name='intermediate_results.json', dict_key='stddev_of_psf') / 1
        reflector_weight = collect_data(directory=directory, file_name='intermediate_results.json', dict_key='reflector_weight') / 450
        tension_ring_weight = collect_data(directory=directory, file_name='intermediate_results.json', dict_key='tension_ring_weight') / 187
        max_final_deformation = collect_data(directory=directory, file_name='intermediate_results.json', dict_key='max_final_deformation') / 0.6
        g1.set_ydata(fitness_function)
        g1.set_xdata(range(len(fitness_function)))
        g2.set_ydata(stddev_of_psf)
        g2.set_xdata(range(len(stddev_of_psf)))
        g3.set_ydata(reflector_weight)
        g3.set_xdata(range(len(reflector_weight)))
        g4.set_ydata(tension_ring_weight)
        g4.set_xdata(range(len(tension_ring_weight)))
        g5.set_ydata(max_final_deformation)
        g5.set_xdata(range(len(max_final_deformation)))
        ax.relim()
        ax.autoscale()
        plt.draw()
        plt.pause(60)


def create_history_of_data(directory=directory, file_name='intermediate_results.json', dict_key='stddev_of_psf'):
    dict_data=collect_data(directory, file_name, dict_key)
    min_dict_data=dict_data.min()
    iter_number_of_min_dict_data = np.argmin(dict_data)
    plt.bar(left=np.arange(len(dict_data)), height=dict_data, width=1.0, color='green')
    #plt.bar(left=np.arange(10, 1260, 50), height=dict_data, width=30.0, color='green')
    plt.xlabel('Iteration number')
    plt.ylabel(str(dict_key))
    plt.title('Progress of PSO. Best iteration:'+str(iter_number_of_min_dict_data)+' with '+dict_key+': '+str(min_dict_data))
    plt.xlim(xmin=0)
    plt.grid(True)

    #plt.savefig('C:\\Users\\Spiros Daglas\\Desktop\\'+dict_key+'.png', bbox_inches='tight')

    plt.show()
    #return dict_data

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

inputPoints = collect_pareto_points(directory)[:,:3].tolist()
paretoPoints, dominatedPoints = simple_cull(inputPoints, dominates)

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
    plt.ylim(ymax=2)
    plt.show()
