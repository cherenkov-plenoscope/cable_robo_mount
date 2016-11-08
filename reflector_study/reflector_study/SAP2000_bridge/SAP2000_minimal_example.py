import os
import sys
import comtypes.client
import numpy as np


#set the following flag to true to attach to an existing instance of the program
#otherwise a new instance of the program will be started
AttachToInstance = False # True #
#full path to the program executable
#set it to the installation folder
ProgramPath = 'C:\Program Files\Computers and Structures\SAP2000 18\sap2000.exe'

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
MATERIAL_CONCRETE = 2
MATERIAL_NODESIGN = 3
MATERIAL_ALUMINUM = 4
MATERIAL_COLDFORMED = 5
MATERIAL_REBAR = 6
MATERIAL_TENDON = 7

automatic_material_color = -1
SapModel.PropMaterial.SetMaterial(
    Name= 'Steel_S235',
    MatType= MATERIAL_STEEL,
    Color= automatic_material_color,
    Notes= "S235_Custom-made")

#assign other properties/elasto-plastic behavior
SapModel.PropMaterial.SetOSteel_1(
    Name= "Steel_S235",
    FY= 235000,
    Fu= 360000,
    EFy= 235000, #effective yield strength
    EFu= 360000, #effective ultimate strength
    SSType= 1, #Stress-Strain curve type. 1 if Parametric-Simple, 0 if User-defined
    SSHysType= 2, #Stress-Strain hysteresis type. 0 Elastic, 1 Kinematic, 2 Takeda
    StrainAtHardening= 0.02, #Applies only for parametric Stress-Strain curves, value of SSType 0.
    StrainAtMaxStress= 0.1, #Applies only for parametric Stress-Strain curves, value of SSType 0.
    StrainAtRupture= 0.2, #Applies only for parametric Stress-Strain curves, value of SSType 0.
    FinalSlope= -0.1, #Applies only for parametric Stress-Strain curves, value of SSType 0.
    Temp= 25) #If temperature is assigned in Material properties add a new variable,

SapModel.PropFrame.SetPipe(
    Name= "ROR_42.4x2.6",
    MatProp= "Steel_S235",
    T3= 0.0424,
    Tw= 0.0026,
    Color= automatic_material_color,
    Notes= "pipe 42.4x3.6 according to SIA263")

PointObj_0 = SapModel.PointObj.AddCartesian(
                    X=1.0, Y=1.0, Z=1.0,
                    Name= 'whatever', #it does not matter if a UserName is defined. CHECK return value.
                    UserName='my_point_username_0',
                    CSys='Global',
                    MergeOff=True)

PointObj_1 = SapModel.PointObj.AddCartesian(
                    X=0.0, Y=0.0, Z=0.0,
                    Name='my_point_1',
                    UserName='my_point_username_1',
                    CSys='Global',
                    MergeOff=True)

FrameObj_0 = SapModel.FrameObj.AddByPoint(
                    Point1='my_point_username_0', #Point name
                    Point2='my_point_username_1', #Point name
                    PropName="ROR_42.4x2.6",
                    Name='my_bar_0',
                    UserName='my_username_bar_0')

#assign point object restraints
deegres_of_freedom = [True, True, True, True, True, True] #True is restrained, False is free
SapModel.PointObj.SetRestraint(
    Name= "my_point_username_1", #Point UserName
    Value= deegres_of_freedom,
    ItemType= 0) # 0, 1, 2 for object, group, selected objects in Name


SapModel.LoadPatterns.Add(
    Name= 'Nodal_Forces',
    MyType= 3, #for live loads. For other loads check documentation
    SelfWTMultiplier= 0)
    #AddLoadCase= True) #If true adds also a load case with the same name

SapModel.FrameObj.SetLoadDistributed(
    Name= "my_username_bar_0",
    LoadPat= 'Nodal_Forces',
    MyType= 1, # 0, 1 for Moment per length and Force per legth respectively
    Dir= 10, #direction of force, check documentation. for gravity direction 10
    Dist1= 0, #could be relative or exact
    Dist2= 1, #could be relative or exact
    Val1= 10,
    Val2= 10,
    CSys= "Global",
    RelDist= True, #If true then, Dist1,2 have relative distance values. Else, exact values
    Replace= True, #Replaces existing loads
    ItemType= 0) # 0, 1, 2 for object, group, selected objects in Name


SapModel.PointObj.SetLoadForce(
    Name= "my_point_username_1",
    LoadPat= "Nodal_Forces",
    Value = [0, 0, -40, 0, 0, 0], #in each DOF
    Replace= True, #Replaces existing loads
    CSys= "Global",
    ItemType= 0) # 0, 1, 2 for object, group, selected objects in Name

SapModel.File.Save("C:\\Users\\Spiros Daglas\\Desktop\\asdf\\First_Model_Example")
SapModel.Results.Setup.SetCaseSelectedForOutput("Nodal_Forces")
SapModel.Analyze.RunAnalysis()


NumberResults = 0
Name = "my_point_username_0"
ItemtypeElm = 0
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

[NumberResults, Obj, Elm, LoadCase, StepType, StepNum, U1, U2, U3, R1, R2, R3, ret] = SapModel.Results.JointDispl(
    Name,
    ItemtypeElm, # 0, 1, 2, 3 for object, , element, group, selected objects in Name
    NumberResults,
    Obj, #Creates an array with the object names
    Elm, #Creates an array with the element names
    LoadCase , #Creates an array with the load case names
    StepType , #Creates an array with the step type, if any
    StepNum, #Creates an array with the step number, if any
    U1, U2, U3, #translational deformation
    R1, R2, R3) #roatational deformation

print(U1, U2, U3, R1, R2, R3)
