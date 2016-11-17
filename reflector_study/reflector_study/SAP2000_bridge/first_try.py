import os
import sys
import comtypes.client
import numpy as np

#maybe put in the __init__
from . import config_loading
from .Structural import Structural
from ..Geometry import Geometry
from .. import config
from .. import factory
from .. import tools
from .. import geometry_generator

"""
Comments


-Till now looks like a script. Thinking of how to structure it in this folder.
-An idea is the creation of a tools.py also here and then with another dictionary or config file directly incorporate the geometry in this file. (kind of more clean)
-A new function, which will calculate the nodes according to the bars may be needed. This can reduce the claculation time. Add it in tools and assign it here.
-Group assign increases calculation time for sure and can be avoided, depending on the type of the analysis. Having the nodes in groups saves time later, when more advanced analysis will be run.
-Relative imports can be included in __init__.py. However, not sure about the procedure that should be followed when importing the reflector_study. (I will for sure mess up the relative imports)
-Lists of the assignments can be also avoided, in order to save calculation time. (Not sure if they are needed later)
-All functions that return a value other than 0, 1 were stored in lists. This can change. (see comment above)
-To examine the flow of this script a condition to continue could be implemented, to examine if everything works. (SAP2000 documentation ommits information and some functions do not work as intended to)
-Analysis shown more nodes than expected... (resolve asap)
-Show Sebastian the weird stuff going on with nodes_final and nodes when arranging them for AddPointObj... nodes_final = nodes always(???).However, not important.
"""

class_geometry = Geometry(config.example)
geometry_all = geometry_generator.generate_all(class_geometry)

structural = Structural(config_loading.structural_dict)

#absolutely necessary functions for program initialization
#program starts from the beginning = cannot attach to instance
ProgramPath = 'C:\Program Files\Computers and Structures\SAP2000 18\sap2000.exe'
helper = comtypes.client.CreateObject('Sap2000v18.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v18.cHelper)
SapObject = helper.CreateObject(ProgramPath)
SapObject.ApplicationStart()

SapModel = SapObject.SapModel
kN_m_C = 6
SapModel.InitializeNewModel(kN_m_C) #model is already initialized before but we initialize a new one with new units
SapModel.File.NewBlank() #new blank model/interface

MATERIAL_STEEL = 1
MATERIAL_CONCRETE = 2
MATERIAL_NODESIGN = 3
MATERIAL_ALUMINUM = 4
MATERIAL_COLDFORMED = 5
MATERIAL_REBAR = 6
MATERIAL_TENDON = 7

automatic_material_color = -1
SapModel.PropMaterial.SetMaterial(
    Name= "Steel_S"+str(structural.yielding_point/1000),
    MatType= MATERIAL_STEEL,
    Color= automatic_material_color,
    Notes= "custom-made")

SapModel.PropMaterial.SetOSteel_1(
    Name= "Steel_S"+str(structural.yielding_point/1000),
    FY= structural.yielding_point,
    Fu= structural.ultimate_point,
    EFy= structural.yielding_point, #effective yield strength
    EFu= structural.ultimate_point, #effective ultimate strength
    SSType= 1, #Stress-Strain curve type. 1 if Parametric-Simple, 0 if User-defined
    SSHysType= 2, #Stress-Strain hysteresis type. 0 Elastic, 1 Kinematic, 2 Takeda
    StrainAtHardening= 0.02, #Applies only for parametric Stress-Strain curves, value of SSType 0.
    StrainAtMaxStress= 0.1, #Applies only for parametric Stress-Strain curves, value of SSType 0.
    StrainAtRupture= 0.2, #Applies only for parametric Stress-Strain curves, value of SSType 0.
    FinalSlope= -0.1, #Applies only for parametric Stress-Strain curves, value of SSType 0.
    Temp= 25) #If temperature is assigned in Material properties add a new variable,

SapModel.PropFrame.SetPipe(
    Name= "ROR_"+str(1000 * structural.bar_outter_radius)+"x"+str(1000 * structural.bar_thickness),
    MatProp= "Steel_S"+str(structural.yielding_point/1000),
    T3= structural.bar_outter_radius,
    Tw= structural.bar_thickness,
    Color= automatic_material_color,
    Notes= "pipe according to SIA263")

PointObj = []

for i in range ((geometry_all["bars"].shape[0])):

    start, end = tools.bar_start_and_end_position(geometry_all["nodes"], geometry_all["bars"][i])

    PointObj.append(SapModel.PointObj.AddCartesian(
                        X=start[0],
                        Y=start[1],
                        Z=start[2],
                        Name= 'whatever', #it does not matter if a UserName is defined. CHECK return value.
                        UserName="start_node_of_bar "+str(i),
                        CSys='Global',
                        MergeOff=True))

    PointObj.append(SapModel.PointObj.AddCartesian(
                        X=end[0],
                        Y=end[1],
                        Z=end[2],
                        Name= 'whatever', #it does not matter if a UserName is defined. CHECK return value.
                        UserName="end_node_of_bar "+str(i),
                        CSys='Global',
                        MergeOff=True))


FrameObj = []

for i in range ((geometry_all["bars"].shape[0])):
    FrameObj.append(SapModel.FrameObj.AddByPoint(
                        Point1="start_node_of_bar "+str(i), #Point name
                        Point2="end_node_of_bar "+str(i), #Point name
                        PropName="ROR_42.4x2.6",
                        Name='whatever',
                        UserName='Bar '+str(i)))

SapModel.GroupDef.SetGroup("Restraints")
deegres_of_freedom = [True, True, True, True, True, True] #True is restrained, False is free

Restraint = []

for i in range ((geometry_all["bars"].shape[0])):
    for j in range ((geometry_all["fixtures"].shape[0])):
        if np.all(np.equal(geometry_all["bars"][i][0], geometry_all["fixtures"][j])):
            Restraint.append(SapModel.PointObj.SetRestraint(
                Name= "start_node_of_bar "+str(i), #Point UserName
                Value= deegres_of_freedom,
                ItemType= 0)) # 0, 1, 2 for object, group, selected objects in Name
            SapModel.PointObj.SetGroupAssign(
                Name= "start_node_of_bar "+str(i), #PointObj name
                GroupName=  "Restraints", #Name of the group that the PointObj will be assigned
                Remove= False) #False to assign, True to remove
                #Itemtype= 0) # 0, 1, 2 for object, group, selected objects in Name
        elif np.all(np.equal(geometry_all["bars"][i][1], geometry_all["fixtures"][j])):
            Restraint.append(SapModel.PointObj.SetRestraint(
                Name= "end_node_of_bar "+str(i), #Point UserName
                Value= deegres_of_freedom,
                ItemType= 0)) # 0, 1, 2 for object, group, selected objects in Name
            SapModel.PointObj.SetGroupAssign(
                Name= "end_node_of_bar "+str(i), #PointObj name
                GroupName=  "Restraints", #Name of the group that the PointObj will be assigned
                Remove= False) #False to assign, True to remove
                #Itemtype= 0) # 0, 1, 2 for object, group, selected objects in Name

"""
SapModel.CoordSys.SetCoordSys(
    Name= "position_30", #+str(Geometry(config.example).angle_from_zenith),
    X= 0,Y= 0,Z= 0.0,
    RZ= 0,RY= 0,RX= 30.0) #str(Geometry(config.example).angle_from_zenith))
"""

load_pattern_1_name = 'mirror_tripod_nodal_forces'
SapModel.LoadPatterns.Add(
    Name= load_pattern_1_name,
    MyType= 3, #for live loads. For other loads check documentation
    SelfWTMultiplier= 0)
    #AddLoadCase= True) #If true adds also a load case with the same name

SapModel.GroupDef.SetGroup("Tripod_nodes")

for i in range ((geometry_all["bars"].shape[0])):
    for j in range((geometry_all["mirror_tripods"].shape[0])):
        for k in range (geometry_all["mirror_tripods"].shape[1]):
            if np.all(np.equal(geometry_all["bars"][i][0], geometry_all["mirror_tripods"][j][k])):
                SapModel.PointObj.SetLoadForce(
                    Name= "start_node_of_bar "+str(i),
                    LoadPat= load_pattern_1_name,
                    Value = [0, 0, -0.6, 0, 0, 0], #in each DOF
                    Replace= True, #Replaces existing loads
                    CSys= "Global",
                    ItemType= 0) # 0, 1, 2 for object, group, selected objects in Name
                SapModel.PointObj.SetGroupAssign(
                    Name= "start_node_of_bar "+str(i), #PointObj name
                    GroupName=  "Tripod_nodes", #Name of the group that the PointObj will be assigned
                    Remove= False) #False to assign, True to remove
                    #Itemtype= 0) # 0, 1, 2 for object, group, selected objects in Name
            elif np.all(np.equal(geometry_all["bars"][i][1], geometry_all["mirror_tripods"][j][k])):
                SapModel.PointObj.SetLoadForce(
                    Name= "end_node_of_bar "+str(i),
                    LoadPat= load_pattern_1_name,
                    Value = [0, 0, -0.6, 0, 0, 0], #in each DOF
                    Replace= True, #Replaces existing loads
                    CSys= "Global",
                    ItemType= 0) # 0, 1, 2 for object, group, selected objects in Name
                SapModel.PointObj.SetGroupAssign(
                    Name= "end_node_of_bar "+str(i), #PointObj name
                    GroupName=  "Tripod_nodes", #Name of the group that the PointObj will be assigned
                    Remove= False) #False to assign, True to remove
                    #Itemtype= 0) # 0, 1, 2 for object, group, selected objects in Name

"""
SapModel.SetPresentCoordSystem(
    CSys= "position_30") #+str(Geometry(config.example).angle_from_zenith))
"""

SapModel.File.Save("C:\\Users\\Spiros Daglas\\Desktop\\asdf\\First_Model_Example")
SapModel.Results.Setup.SetCaseSelectedForOutput(load_pattern_1_name)
SapModel.Analyze.RunAnalysis()

NumberResults = 0
Name = "Tripod_nodes"
mtypeElm = 2
Obj = []
Elm = []
LoadCase = []
StepType = []
StepNum = []
U1 = []
U2 = []
U3 = []
R1 = []
R2 = []
R3 = []

[NumberResults,
Obj,
Elm,
LoadCase,
StepType,
StepNum,
U1, U2, U3,
R1, R2, R3,
ret] = SapModel.Results.JointDispl(
            Name,
            mtypeElm, # 0, 1, 2, 3 for object, element, group, selected objects in Name
            NumberResults,
            Obj, #Creates an array with the object names
            Elm, #Creates an array with the element names
            LoadCase , #Creates an array with the load case names
            StepType , #Creates an array with the step type, if any
            StepNum, #Creates an array with the step number, if any
            U1, U2, U3, #translational deformation
            R1, R2, R3) #roatational deformation

Displacements_of_mirror_tripod_nodes = [Obj] + [U1] + [U2] + [U3] + [R1] + [R2] + [R3]
