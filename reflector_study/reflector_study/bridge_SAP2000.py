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
#full path to the model
#set it to the desired path of your model
APIPath = 'C:\Users\Spiros Daglas\polybox\ETHZ\5. Semester\TelescopeProject_Master Thesis_HS16\2.Python\reflector_study\reflector_study\SAP2000_output'
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

#add frame object by coordinates
#(xi, yi, zi, xj, yj, zj, Name, PropName, UserName, CSys)
SapModel.FrameObj.AddByCoord(0,0,0,1.039,-0.6,-1.191,"FrameN1","ROR_42.4x2.6","1","Global")
SapModel.FrameObj.AddByCoord(1.039,-0.6,-1.191,2.079,-1.2,0.019,"FrameN2","ROR_42.4x2.6","2","Global")


#refresh view, update (initialize) zoom
SapModel.View.RefreshView(0, False)


#Define new group
SapModel.GroupDef.SetGroup("Group_Restraints")
Group_Restraints = "Group_Restraints"

#Select all objects in the same XY plane as the point number in brackets
SapModel.SelectObj.PlaneXY("2151")

#Assign selected points in the group specified
SapModel.PointObj.SetGroupAssign("ignore", "Group_Restraints", False, 2)

#Set restraints according to group
Einspannung = [True, True, True, True, True, True]
SapModel.PointObj.setRestraint(Group_Restraints, Einspannung, 1)

#refresh view, update (initialize) zoom
ret = SapModel.View.RefreshView(0, False)

#Add new load pattern and the respective load case
#(Name, load type eg 1 for dead, 3 for live, 6 for wind or 5 for quake, SW multiplier, AddloadCase with the same name as the Load Pattern if True)
SapModel.LoadPatterns.Add('Nodal_Forces', 3, 2, True)


"""
#Add new load pattern and the respective load case
#(Name, load type eg 1 for dead, 3 for live, 6 for wind or 5 for quake, SW multiplier, AddloadCase with the same name as the Load Pattern if True)
SapModel.LoadPatterns.Add('Nodal_Forces', 3, 0, True)

#Assign upper nodes group
SapModel.GroupDef.SetGroup("Upper_Nodes")
Group_Restraints = "Upper_Nodes"

#Set nodal force to point objects of a group
Force_Value = [0, 0, -0.6, 0, 0, 0]
SapModel.PointObj.SetLoadForce("Upper_Nodes", "Nodal_Forces", Force_Value, True, "Global", 1)
"""
#save model
SapModel.File.Save("C:\\Users\\Spiros Daglas\\Desktop\\RR\\Space_Frame_analysis")
#clear all case and combo output selections
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
#set case and combo output selections
SapModel.Results.Setup.SetCaseSelectedForOutput("Nodal_Forces")
#Analysis Run
SapModel.Analyze.RunAnalysis()

#Preliminary functions for return values
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
[NumberResults, Obj, Elm, ACase, StepType, StepNum, U1, U2, U3, R1, R2, R3, ret] = SapModel.Results.JointDispl("2088", 0, NumberResults, Obj, Elm, "Nodal_Forces", StepType, StepNum, U1, U2, U3, R1, R2, R3)
#print Results
print(U1, U2, U3, R1, R2, R3)

"""
#assign loading for load pattern "Nodal_Forces"
#(Name, Load pattern name, Force/L for 1 or Moment/L for 2, 4or5or6 for XYZ in the Global CS, Dist1(0 for start), Dist2(1 for end), LoadValue1, LoadValue2, CSys name, RelDist(True), Replace previous assignments(True), ItemType 0 for object or 1 for group or 2 for selectedobjects)
SapModel.FrameObj.SetLoadDistributed(F1, 'Nodal_Forces', 1, 4, 0, 1, 10, 10, "Global", True, True, 0)
#save model
SapModel.File.Save("C:\\Users\\spyro\\Desktop\\RR\\Space_Frame_analysis")
#clear all case and combo output selections
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
#set case and combo output selections
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")
#Analysis Run
SapModel.Analyze.RunAnalysis()
#Preliminary functions for return values
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
[NumberResults, Obj, Elm, ACase, StepType, StepNum, U1, U2, U3, R1, R2, R3, ret] = SapModel.Results.JointDispl("2", 0, NumberResults, Obj, Elm, "DEAD", StepType, StepNum, U1, U2, U3, R1, R2, R3)
#print Results
print(U1, U2, U3, R1, R2, R3)
#close Sap2000
SapObject.ApplicationExit(False)
"""
