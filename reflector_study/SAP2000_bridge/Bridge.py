import os
import sys
import comtypes.client
import numpy as np


class Bridge(object):

    def __init__(self, structural):
        self.structural = structural

        self._helper = comtypes.client.CreateObject("Sap2000v18.Helper").QueryInterface(comtypes.gen.SAP2000v18.cHelper)
        self._SapObject = self._helper.CreateObject(self.structural.SAP_2000_directory)
        self._SapObject.ApplicationStart()
        self._SapModel = self._SapObject.SapModel

        self.initialize_new_workspace()
        self.material_definition()
        self.cross_section_definition()

    def initialize_new_workspace(self):
        Units = 6
        self.new_model = self._SapModel.InitializeNewModel(6)
        self.new_file = self._SapModel.File.NewBlank()

    def material_definition(self):
        steel, concrete = 1, 2
        nodesign, aluminium, coldformed, rebar, tendon = 3, 4, 5, 6, 7
        self._SapModel.PropMaterial.SetMaterial(
            Name= "Steel_S"+str(self.structural.yielding_point/1000), #Divided by 1000 cause we give it in kPa. Notation is in MPa.
            MatType= steel,
            Color= -1,
            Notes= "custom-made")
        self._SapModel.PropMaterial.SetOSteel_1(
            Name= "Steel_S"+str(self.structural.yielding_point/1000), #Divided by 1000 cause we give it in kPa. Notation is in MPa.
            FY= self.structural.yielding_point,
            Fu= self.structural.ultimate_point,
            EFy= self.structural.yielding_point, #effective yield strength
            EFu= self.structural.ultimate_point, #effective ultimate strength
            SSType= 1, #Stress-Strain curve type. 1 if Parametric-Simple, 0 if User-defined
            SSHysType= 2, #Stress-Strain hysteresis type. 0 Elastic, 1 Kinematic, 2 Takeda
            StrainAtHardening= 0.02, #Applies only for parametric Stress-Strain curves, value of SSType 0.
            StrainAtMaxStress= 0.1, #Applies only for parametric Stress-Strain curves, value of SSType 0.
            StrainAtRupture= 0.2, #Applies only for parametric Stress-Strain curves, value of SSType 0.
            FinalSlope= -0.1, #Applies only for parametric Stress-Strain curves, value of SSType 0.
            Temp= 25) #

    def cross_section_definition(self):
        self._SapModel.PropFrame.SetPipe(
            Name= "ROR_"+str(1000 * self.structural.bar_outter_radius)+"x"+str(1000 * self.structural.bar_thickness),
            MatProp= "Steel_S"+str(self.structural.yielding_point/1000),
            T3= self.structural.bar_outter_radius,
            Tw= self.structural.bar_thickness,
            Color= -1,
            Notes= "pipe according to SIA263")

    def nodes_definition(self, reflector):
        nodes = reflector["nodes"]
        for i in range ((nodes.shape[0])):
            self._SapModel.PointObj.AddCartesian(
                X=nodes[i,0],
                Y=nodes[i,1],
                Z=nodes[i,2],
                Name= 'whatever',
                UserName="node_"+str(i),
                CSys='Global',
                MergeOff=True)

    def frames_definition(self, reflector):
        bars = reflector["bars"]
        for i in range ((bars.shape[0])):
            self._SapModel.FrameObj.AddByPoint(
                Point1="node_"+str(bars[i,0]), #Point name
                Point2="node_"+str(bars[i,1]), #Point name
                PropName="ROR_"+str(1000 * self.structural.bar_outter_radius)+"x"+str(1000 * self.structural.bar_thickness),
                Name='whatever',
                UserName='bar_'+str(i))

    def restraints_definition(self, reflector):
        fixtures = reflector["fixtures"]
        deegres_of_freedom = [True, True, True, False, False, False]
        for i in range ((fixtures.shape[0])):
            self._SapModel.PointObj.SetRestraint(
                Name= "node_"+str(fixtures[i]),
                Value= deegres_of_freedom,
                ItemType= 0)

    def group_of_nodes_definition(self, group_name, flat_part_of_reflector):
        self._SapModel.GroupDef.SetGroup(group_name)
        for i in range ((flat_part_of_reflector.shape[0])):
            self._SapModel.PointObj.SetGroupAssign(
                Name= "node_"+str(flat_part_of_reflector[i]), #PointObj name
                GroupName=  group_name, #Name of the group that the PointObj will be assigned
                Remove= False)

    def load_scenario_dead(self, load_pattern_name= "dead_load"):
        self._SapModel.LoadPatterns.Add(
            Name= load_pattern_name,
            MyType= 1,
            SelfWTMultiplier= 1)

    def load_scenario_facet_weight(self, reflector, load_pattern_name= "facets_live_load"):
        mirror_tripods = reflector["mirror_tripods"]
        self._SapModel.LoadPatterns.Add(
            Name= load_pattern_name,
            MyType= 3,
            SelfWTMultiplier= 0)
        for i in range((mirror_tripods.shape[0])):
            for j in range((mirror_tripods.shape[1])):
                self._SapModel.PointObj.SetLoadForce(
                    Name= "node_"+str(mirror_tripods[i,j]),
                    LoadPat= load_pattern_name,
                    Value = [0, 0, -self.structural.tripod_nodes_weight, 0, 0, 0], #in each DOF
                    Replace= True, #Replaces existing loads
                    CSys= "Global",
                    ItemType= 0) # 0, 1, 2

    def load_combination_2LP_definition(self, CName1= "dead_load", CName2= "facets_live_load", load_combination_name= "dead+live"):
        self._SapModel.RespCombo.Add(
            Name= load_combination_name,
            ComboType= 0)
        self._SapModel.RespCombo.SetCaseList(load_combination_name, 0, CName1, 1.35)
        self._SapModel.RespCombo.SetCaseList(load_combination_name, 0, CName2, 1.5)

    def save_model(self, path= "C:\\Users\\Spiros Daglas\\Desktop\\asdf\\First_Model_Example"):
        self._SapModel.File.Save(path)

    def run_analysis(self):
        self.save_model()
        self._SapModel.Analyze.RunAnalysis()

    def get_displacements_for_group_of_nodes_for_selected_load_pattern(self, load_pattern_name, group_name= "ALL"):
        self._SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
        self._SapModel.Results.Setup.SetCaseSelectedForOutput(load_pattern_name)

        NumberResults = 0
        Name = group_name
        mtypeElm = 2
        Obj, Elm = [], []
        LoadCase, StepType, StepNum = [], [], []
        U1, U2, U3, R1, R2, R3 = [], [], [], [], [], []

        [NumberResults, Obj, Elm,
        LoadCase, StepType, StepNum,
        U1, U2, U3, R1, R2, R3,
        ret] = self._SapModel.Results.JointDispl(
                    Name, mtypeElm, NumberResults,
                    Obj, Elm,
                    LoadCase, StepType, StepNum,
                    U1, U2, U3, R1, R2, R3)
        relative_displacements = []
        for i in range(len(Obj)):
            relative_displacements.append([Obj[i], U1[i], U2[i], U3[i], R1[i], R2[i], R3[i]])
        return relative_displacements

    def get_displacements_for_group_of_nodes_for_selected_load_combination(self, load_combination_name, group_name= "ALL"):
        self._SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
        self._SapModel.Results.Setup.SetComboSelectedForOutput(load_combination_name)

        NumberResults = 0
        Name = group_name
        mtypeElm = 2
        Obj, Elm = [], []
        LoadCase, StepType, StepNum = [], [], []
        U1, U2, U3, R1, R2, R3 = [], [], [], [], [], []

        [NumberResults, Obj, Elm,
        LoadCase, StepType, StepNum,
        U1, U2, U3, R1, R2, R3,
        ret] = self._SapModel.Results.JointDispl(
                    Name, mtypeElm, NumberResults,
                    Obj, Elm,
                    LoadCase, StepType, StepNum,
                    U1, U2, U3, R1, R2, R3)
        relative_displacements = []
        for i in range(len(Obj)):
            relative_displacements.append([Obj[i], U1[i], U2[i], U3[i], R1[i], R2[i], R3[i]])
        return relative_displacements

    def get_forces_for_group_of_bars_for_selected_load_pattern(self, load_pattern_name, group_name= "ALL"):
        self._SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
        self._SapModel.Results.Setup.SetCaseSelectedForOutput(load_pattern_name)

        Name = group_name
        ItemTypeElm = 2
        NumberResults = 0
        Obj, Elm, PointElm = [], [], []
        LoadCase, StepType, StepNum = [], [], []
        P, V2, V3, T, M2, M3 = [], [], [], [], [], []

        [NumberResults, Obj, Elm, PointElm,
        LoadCase, StepType, StepNum,
        P, V2, V3, T, M2, M3,
        ret] = self._SapModel.Results.FrameJointForce(
                    Name, ItemTypeElm, NumberResults,
                    Obj, Elm, PointElm,
                    LoadCase, StepType, StepNum,
                    P, V2, V3, T, M2, M3)
        forces = []
        for i in range(len(Obj)):
            forces.append([Obj[i], PointElm[i], P[i], V2[i], V3[i], T[i], M2[i], M3[i]])
        return forces

    def get_forces_for_group_of_bars_for_selected_load_combination(self, load_combination_name, group_name= "ALL"):
        self._SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
        self._SapModel.Results.Setup.SetComboSelectedForOutput(load_combination_name)

        Name = group_name
        ItemTypeElm = 2
        NumberResults = 0
        Obj, Elm, PointElm = [], [], []
        LoadCase, StepType, StepNum = [], [], []
        P, V2, V3, T, M2, M3 = [], [], [], [], [], []

        [NumberResults, Obj, Elm, PointElm,
        LoadCase, StepType, StepNum,
        P, V2, V3, T, M2, M3,
        ret] = self._SapModel.Results.FrameJointForce(
                    Name, ItemTypeElm, NumberResults,
                    Obj, Elm, PointElm,
                    LoadCase, StepType, StepNum,
                    P, V2, V3, T, M2, M3)
        forces = []
        for i in range(len(Obj)):
            forces.append([Obj[i], PointElm[i], P[i], V2[i], V3[i], T[i], M2[i], M3[i]])
        return forces

    def get_deformed_reflector_for_all_nodes_for_selected_load_pattern(self, reflector, load_pattern_name):
        relative_displacements = self.get_displacements_for_group_of_nodes_for_selected_load_pattern(load_pattern_name)
        nodes_deformed = np.zeros((reflector["nodes"].shape[0],3))
        for i in range(len(relative_displacements)):
            nodes_deformed[i][0] = reflector["nodes"][i][0] + relative_displacements[i][1]
            nodes_deformed[i][1] = reflector["nodes"][i][1] + relative_displacements[i][2]
            nodes_deformed[i][2] = reflector["nodes"][i][2] + relative_displacements[i][3]
        reflector_deformed = reflector.copy()
        reflector_deformed["nodes"] = nodes_deformed
        return reflector, reflector_deformed

    def get_deformed_reflector_for_all_nodes_for_selected_load_combination(self, reflector, load_combination_name):
        relative_displacements = self.get_displacements_for_group_of_nodes_for_selected_load_combination(load_combination_name)
        nodes_deformed = np.zeros((reflector["nodes"].shape[0],3))
        for i in range(len(relative_displacements)):
            nodes_deformed[i][0] = reflector["nodes"][i][0] + relative_displacements[i][1]
            nodes_deformed[i][1] = reflector["nodes"][i][1] + relative_displacements[i][2]
            nodes_deformed[i][2] = reflector["nodes"][i][2] + relative_displacements[i][3]
        reflector_deformed = reflector.copy()
        reflector_deformed["nodes"] = nodes_deformed
        return reflector, reflector_deformed

    def __repr__(self):
        out = "SAP2000_OAPI"
        return out

    def exit_application(self, file_save= "True"):
        self._SapObject.ApplicationExit(file_save)
