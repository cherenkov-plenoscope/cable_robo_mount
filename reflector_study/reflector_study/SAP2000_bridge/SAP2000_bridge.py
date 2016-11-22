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
from .. import non_flat_tools

"""
Comments
-An idea is the creation of a tools.py also here and then with another dictionary or config file directly incorporate the geometry in this file. (kind of more clean)
-Group assign increases calculation time for sure and can be avoided, depending on the type of the analysis. Having the nodes in groups saves time later, when more advanced analysis will be run.
-Relative imports can be included in __init__.py. However, not sure about the procedure that should be followed when importing the reflector_study. (I will for sure mess up the relative imports)
-Lists of the assignments can be also avoided, in order to save calculation time. (Not sure if they are needed later)
-All functions that return a value other than 0, 1 were stored in lists. This can change. (see comment above)
-To examine the flow of this script a condition to continue could be implemented, to examine if everything works. (SAP2000 documentation ommits information and some functions do not work as intended to)
"""

geometry = Geometry(config.example)
structural = Structural(config_loading.structural_dict)

reflector = factory.generate_reflector(geometry)


#def SAP_2000_bridge(reflector, structural):
nodes = reflector["nodes"]
joints = reflector["joints"]
bars = reflector["bars"]
mirror_tripods = reflector["mirror_tripods"]
fixtures = reflector["fixtures"]

#absolutely necessary functions for program initialization
#program starts from the beginning = cannot attach to instance
ProgramPath = structural.SAP_2000_directory
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
    Name= "Steel_S"+str(structural.yielding_point/1000), #Divided by 1000 cause we give it in kPa. Notation is in MPa.
    MatType= MATERIAL_STEEL,
    Color= automatic_material_color,
    Notes= "custom-made")
SapModel.PropMaterial.SetOSteel_1(
    Name= "Steel_S"+str(structural.yielding_point/1000), #Divided by 1000 cause we give it in kPa. Notation is in MPa.
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
for i in range ((nodes.shape[0])):
    PointObj.append(SapModel.PointObj.AddCartesian(
                        X=nodes[i,0],
                        Y=nodes[i,1],
                        Z=nodes[i,2],
                        Name= 'whatever', #it does not matter if a UserName is defined. CHECK return value.
                        UserName="node_"+str(i),
                        CSys='Global',
                        MergeOff=True))
FrameObj = []
for i in range ((bars.shape[0])):
    FrameObj.append(SapModel.FrameObj.AddByPoint(
                        Point1="node_"+str(bars[i,0]), #Point name
                        Point2="node_"+str(bars[i,1]), #Point name
                        PropName="ROR_"+str(1000 * structural.bar_outter_radius)+"x"+str(1000 * structural.bar_thickness),
                        Name='whatever',
                        UserName='bar_'+str(i)))
SapModel.GroupDef.SetGroup("Restraints")
deegres_of_freedom = [True, True, True, True, True, True] #True is restrained, False is free
Restraint = []
for i in range ((fixtures.shape[0])):
    SapModel.PointObj.SetRestraint(
        Name= "node_"+str(fixtures[i]), #Point UserName
        Value= deegres_of_freedom,
        ItemType= 0) # 0, 1, 2 for object, group, selected objects in Name
    SapModel.PointObj.SetGroupAssign(
        Name= "node_"+str(fixtures[i]), #PointObj name
        GroupName=  "Restraints", #Name of the group that the PointObj will be assigned
        Remove= False) #False to assign, True to remove
        #Itemtype= 0) # 0, 1, 2 for object, group, selected objects in Name
load_pattern_1_name = "facets_weight_on_mirror_tripod_nodes"
SapModel.LoadPatterns.Add(
    Name= load_pattern_1_name,
    MyType= 3, #for live loads. For other loads check documentation
    SelfWTMultiplier= 0)
    #AddLoadCase= True) #If true adds also a load case with the same name
SapModel.GroupDef.SetGroup("Tripod_nodes")
for i in range((mirror_tripods.shape[0])):
    for j in range((mirror_tripods.shape[1])):
        SapModel.PointObj.SetLoadForce(
            Name= "node_"+str(mirror_tripods[i,j]),
            LoadPat= load_pattern_1_name,
            Value = [0, 0, -structural.tripod_nodes_weight, 0, 0, 0], #in each DOF
            Replace= True, #Replaces existing loads
            CSys= "Global",
            ItemType= 0) # 0, 1, 2 for object, group, selected objects in Name
        SapModel.PointObj.SetGroupAssign(
            Name= "node_"+str(mirror_tripods[i,j]), #PointObj name
            GroupName=  "Tripod_nodes", #Name of the group that the PointObj will be assigned
            Remove= False) #False to assign, True to remove
            #Itemtype= 0) # 0, 1, 2 for object, group, selected objects in Name
<<<<<<< HEAD

SapModel.File.Save("C:\\Users\\Spiros Daglas\\Desktop\\asdf\\First_Model_Example")
SapModel.Results.Setup.SetCaseSelectedForOutput(load_pattern_1_name)
SapModel.Analyze.RunAnalysis()
=======
    load_pattern_0_name = "self_weight"
    load_pattern_1_name = "facets_weight_on_mirror_tripod_nodes"
    SapModel.LoadPatterns.Add(
        Name= load_pattern_0_name,
        MyType= 1, #for live loads. For other loads check documentation
        SelfWTMultiplier= 1)
        #AddLoadCase= True) #If true adds also a load case with the same name
    SapModel.LoadPatterns.Add(
        Name= load_pattern_1_name,
        MyType= 3, #for live loads. For other loads check documentation
        SelfWTMultiplier= 0)
    SapModel.GroupDef.SetGroup("Tripod_nodes")
    for i in range((mirror_tripods.shape[0])):
        for j in range((mirror_tripods.shape[1])):
            SapModel.PointObj.SetLoadForce(
                Name= "node_"+str(mirror_tripods[i,j]),
                LoadPat= load_pattern_1_name,
                Value = [0, 0, -structural.tripod_nodes_weight, 0, 0, 0], #in each DOF
                Replace= True, #Replaces existing loads
                CSys= "Global",
                ItemType= 0) # 0, 1, 2 for object, group, selected objects in Name
            SapModel.PointObj.SetGroupAssign(
                Name= "node_"+str(mirror_tripods[i,j]), #PointObj name
                GroupName=  "Tripod_nodes", #Name of the group that the PointObj will be assigned
                Remove= False) #False to assign, True to remove
                #Itemtype= 0) # 0, 1, 2 for object, group, selected objects in Name

    SapModel.File.Save("C:\\Users\\Spiros Daglas\\Desktop\\asdf\\First_Model_Example")
    SapModel.Results.Setup.SetCaseSelectedForOutput(load_pattern_0_name)
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
>>>>>>> cdf3485d0f52d1c0e64aa7b463a676dfe94574d3

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

Name = "ALL"
ItemTypeElm = 2
NumberResults = 0
Obj = []
Elm = []
PointElm= []
LoadCase = []
StepType = []
StepNum = []
P= []
V2= []
V3= []
T= []
M2= []
M3= []
[NumberResults,
Obj,
Elm,
PointElm,
LoadCase,
StepType,
StepNum,
P, V2, V3,
T, M2, M3,
ret] = SapModel.Results.FrameJointForce(
            Name ,
            ItemTypeElm ,
            NumberResults ,
            Obj ,
            Elm ,
            PointElm ,
            LoadCase ,
            StepType ,
            StepNum ,
            P, V2, V3,
            T, M2, M3)
Nodal_forces_of_all_bars = [Obj] + [PointElm] + [P] + [V2] + [V3] + [T] + [M2] + [M3]

Name = "Restraints"
ItemTypeElm = 2
NumberResults = 0
Obj = []
Elm = []
LoadCase = []
StepType = []
StepNum = []
F1= []
F2= []
F3= []
M1= []
M2= []
M3= []
[NumberResults,
Obj,
Elm,
LoadCase,
StepType,
StepNum,
F1, F2, F3,
M1, M2, M3,
ret] = SapModel.Results.JointReact(
            Name ,
            ItemTypeElm ,
            NumberResults ,
            Obj ,
            Elm ,
            LoadCase ,
            StepType ,
            StepNum ,
            P, V2, V3,
            T, M2, M3)
Reactions_of_fixtures_on_tension_ring = [Obj] + [F1] + [F2] + [F3] + [M1] + [M2] + [M3]

#    return Displacements_of_mirror_tripod_nodes, Nodal_Forces , Reactions_of_fixtures_on_tension_ring
