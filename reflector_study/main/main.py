import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import csv

from . import coordinate_systems as cs
from . import plotting_tools as pt
from . import generate_plot_bars as gpb
from . import statistical_data as sd
from . import mirror_tripods as mt
from . import plot_bars_from_xyz_coordinates as pbxyz

#for SAP2000 bridge
import os
import sys
import comtypes.client
import subprocess



#Dimensions of 3D array with 3 values for the i, j, k coordinates

#remember to define these supposed_i,j,k values from the facet size and radius of the dish.
#they play an important role in the grid mesh definition, according to the w,h of the facet

#check the different inputs throughout and then gather them here

#these are actually the number of nodes in each direction
#like x axis
supposed_i = 8
#like y axis
supposed_j = 8
#like z axis
supposed_k = 2 #represents the intermediate gaps. the layer surfaces are supposed_k+1

offset_in_x_dir = 0.5 #In the initial model half base raster
offset_in_y_dir = 0.5 #In the initial model half base raster

lattice_grid = np.zeros((2*supposed_i-1, 2*supposed_j-1, 2*supposed_k-1, 3))

for i in range(-supposed_i, supposed_i):
    for j in range(-supposed_j, supposed_j):
        for k in range(-supposed_k, 1):
            lattice_grid[i,j,k] = (i, j, k)
            lattice_grid[i,j,k] = lattice_grid[i,j,k] + (offset_in_x_dir*k, offset_in_y_dir*k, 0)

lattice_grid_x = lattice_grid[:,:,:,0].ravel()
lattice_grid_y = lattice_grid[:,:,:,1].ravel()
lattice_grid_z = lattice_grid[:,:,:,2].ravel()

pt.plot_scatter(lattice_grid_x, lattice_grid_y, lattice_grid_z)
#pt.plot_wireframe(lattice_grid_x, lattice_grid_y, lattice_grid_z)

#From now on we transform to cartesian without the z coordinates

for i in range(-supposed_i, supposed_i):
    for j in range(-supposed_j, supposed_j):
        for k in range(-supposed_k, 1):
            lattice_grid[i,j,k] = cs.hcp_lattice_to_cartesian(i, j, k, scale =1)
            #WTF(1) finds the difference between the coordinates of the previous layer in x or y and multiplies with the given offset
            #then for each layer(k) adds up the previous coordiantes as the offset(which remains stable) mal k(#layer)
            if k == 0:
                lattice_grid[i,j,k] = cs.hcp_lattice_to_cartesian(i, j, k, scale =1) #, offset_in_x_dir, offset_in_y_dir)
            else:
                offset_x = (cs.hcp_lattice_to_cartesian(i+1, j, k-1, scale =1)[0]-cs.hcp_lattice_to_cartesian(i, j, k-1, scale =1)[0])*offset_in_x_dir
                offset_y = (cs.hcp_lattice_to_cartesian(i, j+1, k-1, scale =1)[1]-cs.hcp_lattice_to_cartesian(i, j, k-1, scale =1)[1])*offset_in_y_dir
                lattice_grid[i,j,k,0] = cs.hcp_lattice_to_cartesian(i, j, k-1, scale =1)[0] + offset_x*k
                lattice_grid[i,j,k,1] = cs.hcp_lattice_to_cartesian(i, j, k-1, scale =1)[1] + offset_y*k

lattice_grid_x = lattice_grid[:,:,:,0].ravel()
lattice_grid_y = lattice_grid[:,:,:,1].ravel()
lattice_grid_z = lattice_grid[:,:,:,2].ravel()

pt.plot_scatter(lattice_grid_x, lattice_grid_y, lattice_grid_z)
#pt.plot_wireframe(lattice_grid_x, lattice_grid_y, lattice_grid_z)


#From now on we transform to cartesian with the z coordinates
#Inputs needed
scale = 1.2 #Default is also 1. REPRESENTS THE FACET APOTHEM
focal_length = 75 #Default is 1
dc_over_pa = 0 #Default is 0
space_frame_layer_distance = 1.2 #Distance betwwen the space frame layers

for i in range(-supposed_i, supposed_i-1):
    for j in range(-supposed_j, supposed_j-1):
        for k in range(-supposed_k, 1):
            x_position = lattice_grid[i,j,k,0]
            y_position = lattice_grid[i,j,k,1]

            lattice_grid[i,j,k] = cs.hcp_parabolic_transformation(k, x_position, y_position, focal_length, dc_over_pa, scale)
            lattice_grid[i,j,k,2] = lattice_grid[i,j,k,2]*space_frame_layer_distance


lattice_grid_x = lattice_grid[:,:,:,0].ravel()
lattice_grid_y = lattice_grid[:,:,:,1].ravel()
lattice_grid_z = lattice_grid[:,:,:,2].ravel()

pt.plot_scatter(lattice_grid_x, lattice_grid_y, lattice_grid_z)
#pt.plot_wireframe(lattice_grid_x, lattice_grid_y, lattice_grid_z)

#Cookie cutter
#Input dish radius
dish_radius = 6

for i in range(-supposed_i, supposed_i):
    for j in range(-supposed_j, supposed_j):
        for k in range(-supposed_k, supposed_k):
            if cs.nodal_distance_in_polar_coordinates(i, j, k, lattice_grid) > dish_radius:
                lattice_grid[i,j,k] = ["NaN", "NaN", "NaN"]
            else:
                lattice_grid[i,j,k] = lattice_grid[i,j,k]

lattice_grid_x = lattice_grid[:,:,:,0].ravel()
lattice_grid_y = lattice_grid[:,:,:,1].ravel()
lattice_grid_z = lattice_grid[:,:,:,2].ravel()


pt.plot_scatter(lattice_grid_x, lattice_grid_y, lattice_grid_z)
#pt.plot_wireframe(lattice_grid_x, lattice_grid_y, lattice_grid_z)

#Till here according to plot seems fine


bars = gpb.bars(supposed_i, supposed_j, supposed_k, lattice_grid)
#gpb.plot_bars(bars, lattice_grid)

"""
#lattice_grid without the NaN

lattice_grid_x = lattice_grid_x[~np.isnan(lattice_grid_x)]
lattice_grid_y = lattice_grid_y[~np.isnan(lattice_grid_y)]
lattice_grid_z = lattice_grid_z[~np.isnan(lattice_grid_z)]

lattice_grid = np.vstack((lattice_grid_x, lattice_grid_y, lattice_grid_z)).T
"""

#Stupid part of code. Does nothing. node_numbers_ijk are actually the same as bars
"""
#calculates which node belongs to each bar in i,j,k coordinates
def ijk_start_and_end_of_bar(i, bars):
    start_node_ijk =  bars[i,0]
    end_node_ijk =  bars[i,1]

    return start_node_ijk, end_node_ijk

#creates an array with the start and end nodal coordinates in i,j,k. First dimension of the array is the bar number/label.
node_numbers_ijk = np.zeros((bars.shape[0],2,3))

for i in range(bars.shape[0]):
    node_numbers_ijk[i,0] = ijk_start_and_end_of_bar(i, bars)[0]
    node_numbers_ijk[i,1] = ijk_start_and_end_of_bar(i, bars)[1]
"""
#calculates the x,y,z coordinates with the aforementioned i,j,k coordinates as indexes in the lattice_grid
start_node_xyz = np.zeros((bars.shape[0],3))
end_node_xyz = np.zeros((bars.shape[0],3))

for i in range(bars.shape[0]):
    try:
        start_node_xyz[i] = lattice_grid[bars[i,0,0], bars[i,0,1], bars[i,0,2]]
        end_node_xyz[i] = lattice_grid[bars[i,1,0], bars[i,1,1], bars[i,1,2]]
    except IndexError:
        pass

#creates an array with the start and end nodal coordinates in x,y,z. First dimension of the array is the bar number/label.
#the all_bars one will remain as it is with all bars, whereas the normal one will have the final bars. (very long bars out)

node_numbers_xyz = np.zeros((bars.shape[0],2,3))
node_numbers_xyz_all_bars = np.zeros((bars.shape[0],2,3))

for i in range(bars.shape[0]):
    node_numbers_xyz[i,0] = start_node_xyz[i]
    node_numbers_xyz[i,1] = end_node_xyz[i]
    node_numbers_xyz_all_bars[i,0] = start_node_xyz[i]
    node_numbers_xyz_all_bars[i,1] = end_node_xyz[i]

#calculate the lengths of the bars (initially)
lengths = sd.lengths_of_bars(bars, node_numbers_xyz)

#Bars control. Elimination of unwanted long bars. Code will work even for other dish geometries but check the results.
if scale*np.sqrt(3) > np.sqrt((offset_in_x_dir*scale)**2+(offset_in_y_dir*np.sqrt(3)*scale)**2+space_frame_layer_distance**2):
    controler_bars = 1  #in most cases is 1, cause the offset is 0.5 and the distance between the layers significantlly smaller than grid distance in y axis
else:
    controler_bars = 0

#Input a threshold value that will take into account the curvature or imperfections of the dish geomtery
threshold_due_to_curvature = 0.3

if controler_bars == 1:
    max_bar_length = scale*np.sqrt(3) + threshold_due_to_curvature
else:
    max_bar_length = np.sqrt((offset_in_x_dir*scale)**2+(offset_in_y_dir*np.sqrt(3)*scale)**2+space_frame_layer_distance**2) + threshold_due_to_curvature

#if the bar is too long then a nan value is added
for i in range(bars.shape[0]):
    if lengths[i] >= max_bar_length:
        node_numbers_xyz[i] = [["NaN","NaN","NaN"], ["NaN","NaN","NaN"]]


#If a start/end node is nan then the other one (start/end) becomes nan too
for i in range(bars.shape[0]):
    if np.any(np.isnan(node_numbers_xyz[i,0]))  or np.any(np.isnan(node_numbers_xyz[i,1])):
        node_numbers_xyz[i,0] = ["NaN","NaN","NaN"]
        node_numbers_xyz[i,1] = ["NaN","NaN","NaN"]
    if np.any(np.isnan(node_numbers_xyz_all_bars[i,0]))  or np.any(np.isnan(node_numbers_xyz_all_bars[i,1])):
        node_numbers_xyz_all_bars[i,0] = ["NaN","NaN","NaN"]
        node_numbers_xyz_all_bars[i,1] = ["NaN","NaN","NaN"]

#calculate the lengths of the bars (finally, without the long bars for normal. put all_bars for comparison)
lengths = sd.lengths_of_bars(bars, node_numbers_xyz)

#cleaning lengths list from NaN values
lengths[np.isnan(lengths)] = 0
lengths_clean = lengths[np.nonzero(lengths)]

#plot a histogram of the lengths of the bars
sd.plot_histogram_of_bars(lengths_clean)

#Check how many bars are out because they are long

node_numbers_xyz_shape = node_numbers_xyz[~np.any(np.isnan(node_numbers_xyz), axis=2)].shape[0]
node_numbers_xyz_all_bars_shape = node_numbers_xyz_all_bars[~np.any(np.isnan(node_numbers_xyz_all_bars), axis=2)].shape[0]

excluded_long_bars_number = np.absolute(node_numbers_xyz_shape - node_numbers_xyz_all_bars_shape)

#clean the node numbers arrays from nan values
node_numbers_xyz_fin = node_numbers_xyz[~np.any(np.isnan(node_numbers_xyz), axis=2)]
node_numbers_xyz_all_bars_fin = node_numbers_xyz_all_bars[~np.any(np.isnan(node_numbers_xyz_all_bars), axis=2)]

#Mirror tripods calculation
mirror_tripods = mt.mirror_tripods(supposed_i, supposed_j, supposed_k, lattice_grid)
mt.plot_mirror_tripods(mirror_tripods, lattice_grid, bars)

#calculate the coordinates of the mirror tripods in the first layer. create an array with [nodes,3] shape
facet_supporting_nodes = np.zeros((mirror_tripods.shape[0]*2,3))

for i in range(mirror_tripods.shape[0]):
    facet_supporting_nodes[i] = mirror_tripods[i,0]
    facet_supporting_nodes[i + mirror_tripods.shape[0]] = mirror_tripods[i,1]

facet_supporting_nodes_xyz = np.zeros((mirror_tripods.shape[0]*2,3))
for i in range(mirror_tripods.shape[0]*2):
    facet_supporting_nodes_xyz[i] = lattice_grid[int(facet_supporting_nodes[i,0]), int(facet_supporting_nodes[i,1]), int(facet_supporting_nodes[i,2])]

#clean facet_supporting_nodes_xyz from nan
facet_supporting_nodes_xyz = facet_supporting_nodes_xyz[~np.any(np.isnan(facet_supporting_nodes_xyz), axis=1)]
#clean duplicate values
facet_supporting_nodes_xyz = np.vstack({tuple(row) for row in facet_supporting_nodes_xyz})

#plot bars and mirror nodes from the node_numbers_xyz
facet_supporting_nodes_xyz_x = facet_supporting_nodes_xyz[:,0].ravel()
facet_supporting_nodes_xyz_y = facet_supporting_nodes_xyz[:,1].ravel()
facet_supporting_nodes_xyz_z = facet_supporting_nodes_xyz[:,2].ravel()

pbxyz.plot_bars_mirror_nodes_xyz(node_numbers_xyz, facet_supporting_nodes_xyz_x, facet_supporting_nodes_xyz_y, facet_supporting_nodes_xyz_z)

#find the dish supporting nodes

#ALL NODES OF THE FINAL DISH, which means actually replacement of the lattice_grid. (although we keep it)
dish_nodal_coordinates_xyz = np.zeros((node_numbers_xyz.shape[0]*2,3))
for i in range(node_numbers_xyz.shape[0]):
    dish_nodal_coordinates_xyz[i] = node_numbers_xyz[i,0]
    dish_nodal_coordinates_xyz[i + node_numbers_xyz.shape[0]] = node_numbers_xyz[i,1]

#clean dish_nodal_coordinates_xyz from nan
dish_nodal_coordinates_xyz = dish_nodal_coordinates_xyz[~np.any(np.isnan(dish_nodal_coordinates_xyz), axis=1)]
#clean duplicate values
dish_nodal_coordinates_xyz = np.vstack({tuple(row) for row in dish_nodal_coordinates_xyz})
#print for check
dish_nodal_coordinates_xyz_x = dish_nodal_coordinates_xyz[:,0].ravel()
dish_nodal_coordinates_xyz_y = dish_nodal_coordinates_xyz[:,1].ravel()
dish_nodal_coordinates_xyz_z = dish_nodal_coordinates_xyz[:,2].ravel()

#pt.plot_scatter(dish_nodal_coordinates_xyz_x, dish_nodal_coordinates_xyz_y, dish_nodal_coordinates_xyz_z)
#pt.plot_wireframe(dish_nodal_coordinates_xyz_x, dish_nodal_coordinates_xyz_y, dish_nodal_coordinates_xyz_z)

#INPUT HERE. check and change
dish_supporting_nodes_xyz = np.zeros((dish_nodal_coordinates_xyz.shape[0],3))
for i in range(dish_nodal_coordinates_xyz.shape[0]):
    if np.hypot(dish_nodal_coordinates_xyz[i,0], dish_nodal_coordinates_xyz[i,1]) >= (dish_radius - 0.5):
        dish_supporting_nodes_xyz[i] = dish_nodal_coordinates_xyz[i]

#Remove [0,0,0] points
dish_supporting_nodes_xyz = dish_supporting_nodes_xyz[~np.all( dish_supporting_nodes_xyz == 0, axis=1)]

#print for check
dish_supporting_nodes_xyz_x = dish_supporting_nodes_xyz[:,0].ravel()
dish_supporting_nodes_xyz_y = dish_supporting_nodes_xyz[:,1].ravel()
dish_supporting_nodes_xyz_z = dish_supporting_nodes_xyz[:,2].ravel()

#pt.plot_scatter(dish_supporting_nodes_xyz_x, dish_supporting_nodes_xyz_y, dish_supporting_nodes_xyz_z)
#pt.plot_wireframe(dish_supporting_nodes_xyz_x, dish_supporting_nodes_xyz_y, dish_supporting_nodes_xyz_z)



#---------------------------------------------------------------------------------------------------
#THIS SHOULD BE IN ANOTHER FILE (relative import???)

#create a list from the node_numbers_xyz array with the x,y,z coordinates of the bar joints

frames = node_numbers_xyz_fin.tolist()

#according to SAP2000 names create the labels for rest
frame_label = "FrameN"
rest = "ROR_42.4x2.6" , "3", "Global"

SAP2000_frame_objects = []

for i in range(len(frames)-1):
    SAP2000_frame_objects.append (["SapModel.FrameObj.AddByCoord("+",".join(map(str,frames[i])),
                                                                    ",".join(map(str,frames[i+1])),
                                                                    "'"+frame_label+str(i)+"'",
                                                                    "'"+"ROR_42.4x2.6"+"'" ,
                                                                    "'"+str(i)+"'",
                                                                     "'"+"Global"+"'"+")"])

    #print("SapModel.FrameObj.AddByCoord(",",".join(map(str,frames[i])),",".join(map(str,frames[i+1])),",",frame_label,i,",",rest,")")

#print(SAP2000)

csv.register_dialect(
    'SAP2000_dialect',
    delimiter = ',',
    quotechar = '"',
    doublequote = False,
    skipinitialspace = True,
    lineterminator = '\r\n',
    quoting = csv.QUOTE_NONE,
    escapechar=' ')

#write csv file for the import of the frame objects
with open('SAP2000_add_frame_object_by_coordinates.csv', 'w') as mycsvfile:
    thedatawriter = csv.writer(mycsvfile, dialect = "SAP2000_dialect")
    for row in SAP2000_frame_objects:
        thedatawriter.writerow(row)

#select nodes in a range of coordinates
SAP2000_restraints = []

for i in range(dish_supporting_nodes_xyz.shape[0]):
    SAP2000_restraints.append(["SapModel.SelectObj.CoordinateRange("+str(dish_supporting_nodes_xyz[i,0]-0.05),
                                                                    str(dish_supporting_nodes_xyz[i,0]+0.05),
                                                                    str(dish_supporting_nodes_xyz[i,1]-0.05),
                                                                    str(dish_supporting_nodes_xyz[i,1]+0.05),
                                                                    str(dish_supporting_nodes_xyz[i,2]-0.05),
                                                                    str(dish_supporting_nodes_xyz[i,2]+0.05),
                                                                    "False","'"+"Global"+"'", "True", "True",
                                                                    "False","False","False","False"+")"])

#SapModel.SelectObj.CoordinateRange(-5, 5, -5, 5, -10, 10, False, "Global", True, True, False, False, False, False)

#write csv file for the import of the restraints nodes
with open('SAP2000_select_point_object_by_coordinate_range_restraints.csv', 'w') as mycsvfile:
    thedatawriter = csv.writer(mycsvfile, dialect = "SAP2000_dialect")
    for row in SAP2000_restraints:
        thedatawriter.writerow(row)

#select all tripod nodes-facet supporting nodes
SAP2000_mirror_supporting_nodes = []
for i in range(facet_supporting_nodes_xyz.shape[0]):
    SAP2000_mirror_supporting_nodes.append(["SapModel.SelectObj.CoordinateRange("+str(facet_supporting_nodes_xyz[i,0]-0.05),
                                                                                str(facet_supporting_nodes_xyz[i,0]+0.05),
                                                                                str(facet_supporting_nodes_xyz[i,1]-0.05),
                                                                                str(facet_supporting_nodes_xyz[i,1]+0.05),
                                                                                str(facet_supporting_nodes_xyz[i,2]-0.05),
                                                                                str(facet_supporting_nodes_xyz[i,2]+0.05),
                                                                                "False","'"+"Global"+"'", "True", "True",
                                                                                "False","False","False","False"+")"])

#write csv file for the import of the tripod nodes-facet supporting nodes
with open('SAP2000_select_point_object_by_coordinate_range_facet_supports.csv', 'w') as mycsvfile:
    thedatawriter = csv.writer(mycsvfile, dialect = "SAP2000_dialect")
    for row in SAP2000_mirror_supporting_nodes:
        thedatawriter.writerow(row)
"""
#---------------------------------------------------------------------------------------------------
#SAP2000 OAPI engine



#set the following flag to true to attach to an existing instance of the program
#otherwise a new instance of the program will be started
AttachToInstance = False # True #
#full path to the program executable
#set it to the installation folder
ProgramPath = 'C:\Program Files\Computers and Structures\SAP2000 18\sap2000.exe'
#full path to the model
#set it to the desired path of your model
APIPath = 'C:\\Users\\Spiros Daglas\\polybox\\ETHZ\\5. Semester\\TelescopeProject_Master Thesis_HS16\\2.Python\\reflector_study\\reflector_study\\SAP2000_output'
if not os.path.exists(APIPath):
        try:
            os.makedirs(APIPath)
        except OSError:
            pass
ModelPath = APIPath + os.sep + 'output_1.sdb'
if AttachToInstance:
      #attach to a running instance of Sap2000
      try:
            #get the active Sap2000 object
            SapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
      except (OSError, comtypes.COMError):
            print("No running instance of the program found or failed to attach.")
            sys.exit(-1)
else:
      #create a new instance of Sap2000
      try:
            #create OAPI helper object
            helper = comtypes.client.CreateObject('Sap2000v18.Helper')
            helper = helper.QueryInterface(comtypes.gen.SAP2000v18.cHelper)
            #get Sap2000 object
            SapObject = helper.CreateObject(ProgramPath);
      except (OSError, comtypes.COMError):
            print("Cannot start a new instance of the program.")
            sys.exit(-1)
      #start Sap2000 application
      SapObject.ApplicationStart()
#create SapModel object
SapModel = SapObject.SapModel
#initialize model with metric units
kN_m_C = 6
SapModel.InitializeNewModel(kN_m_C)
#Create new blank model
SapModel.File.NewBlank()
#initialize new material property
MATERIAL_STEEL = 1
SapModel.PropMaterial.SetMaterial('Steel_S460', MATERIAL_STEEL, -1, "S460_Custom-made")
#assign other properties/elasto-plastic behavior
SapModel.PropMaterial.SetOSteel_1("Steel_S235", 460000, 460000, 460000, 460000, 1, 2, 0.02, 0.1, 0.2, -0.1)
#set new frame section property/pipe cross sections
#(Name, MatProp, out. Diameter, thickness, Color -1 for random, Notes, GUID not specified)
#CHS 42.4x2.6 EN1993-1-1 or ROR 42.4x2.6 SIA263/C5 Konstruktionstabelle
SapModel.PropFrame.SetPipe("ROR_42.4x2.6", "Steel_S460", 0.0424, 0.0026, -1, "pipe 42.4x3.6 according to SIA263")

#save model
SapModel.File.Save('C:\\Users\\Spiros Daglas\\polybox\\ETHZ\\5. Semester\\TelescopeProject_Master Thesis_HS16\\2.Python\\reflector_study\\reflector_study\\SAP2000_output\\SAP_2000_1')

#add frame object by coordinates
#(xi, yi, zi, xj, yj, zj, Name, PropName, UserName, CSys)

exec(open("./SAP2000_add_frame_object_by_coordinates.csv").read())

#save model
SapModel.File.Save('C:\\Users\\Spiros Daglas\\polybox\\ETHZ\\5. Semester\\TelescopeProject_Master Thesis_HS16\\2.Python\\reflector_study\\reflector_study\\SAP2000_output\\SAP_2000_1')

#refresh view, update (initialize) zoom
SapModel.View.RefreshView(0, False)


#Define new group for the restraints
SapModel.GroupDef.SetGroup("Group_Restraints")
Group_Restraints = "Group_Restraints"

#Select all nodes that will be restrained
exec(open("./SAP2000_select_point_object_by_coordinate_range_restraints.csv").read())

#Assign selected points in the group specified
SapModel.PointObj.SetGroupAssign("ignored", "Group_Restraints", False, 2)

#Set restraints according to group
Einspannung = [True, True, True, True, True, True]
SapModel.PointObj.setRestraint(Group_Restraints, Einspannung, 1)

#clears selection for future use
ClearSelection = SapModel.SelectObj.ClearSelection()

#refresh view, update (initialize) zoom
RefreshView = SapModel.View.RefreshView(0, False)

#Define new group for the facet supporting nodes
SapModel.GroupDef.SetGroup("Group_facet_supports")
Group_facet_supports = "Group_facet_supports"

#Select all nodes that will be grouped
exec(open("./SAP2000_select_point_object_by_coordinate_range_facet_supports.csv").read())

#Assign selected points in the group specified
SapModel.PointObj.SetGroupAssign("ignored", "Group_facet_supports", False, 2)

#clears selection for future use
ClearSelection = SapModel.SelectObj.ClearSelection()

#refresh view, update (initialize) zoom
RefreshView = SapModel.View.RefreshView(0, False)


#Add new load pattern and the respective load case
#(Name, load type eg 1 for dead, 3 for live, 6 for wind or 5 for quake,
# SW multiplier, AddloadCase with the same name as the Load Pattern if True)
SapModel.LoadPatterns.Add('Nodal_Forces', 3, 1, True)

#Set nodal force to point objects of a group
Force_Value = [0, 0, -1.25, 0, 0, 0]
SapModel.PointObj.SetLoadForce("Group_facet_supports", "Nodal_Forces", Force_Value, True, "Global", 1)

#save model
SapModel.File.Save("C:\\Users\\Spiros Daglas\\polybox\\ETHZ\\5. Semester\\TelescopeProject_Master Thesis_HS16\\2.Python\\reflector_study\\reflector_study\\SAP2000_output\\test")

#clear all case and combo output selections
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()

#set case and combo output selections
SapModel.Results.Setup.SetCaseSelectedForOutput("Nodal_Forces")

#Analysis Run
SapModel.Analyze.RunAnalysis()

#Preliminary lists for return values
NumberResults = 0
Obj = []
Elm = []
ACase = []
StepType = []
StepNum = []
U1 = []
U2 = []
U3 = []
R1 = []
R2 = []
R3 = []

#Get joint displacements
[NumberResults,
Obj,
Elm,
ACase,
StepType,
StepNum,
U1, U2, U3, R1, R2, R3,
ret] = SapModel.Results.JointDispl("Group_facet_supports",
                                    2,
                                    NumberResults,
                                    Obj,
                                    Elm,
                                    "Nodal_Forces",
                                    StepType,
                                    StepNum,
                                    U1, U2, U3, R1, R2, R3)
#print Results
#print(U1, U2, U3, R1, R2, R3)

#write csv file with the output values
with open('SAP2000_facet_nodal_deformations.csv', 'w') as mycsvfile:
    thedatawriter = csv.writer(mycsvfile, dialect = "SAP2000_dialect")
    for row in zip(Obj, U1, U2, U3, R1, R2, R3):
        thedatawriter.writerow(row)
"""
