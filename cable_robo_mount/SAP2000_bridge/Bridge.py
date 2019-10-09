import comtypes.client
import numpy as np


class Bridge(object):

    def __init__(self, structural):
        self.structural = structural

        self._SapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
        self._SapModel = self._SapObject.SapModel
        """
        To create new model do the following
        To create new model by starting application do the following
        -----------------

        self._helper = comtypes.client.CreateObject("Sap2000v18.Helper").QueryInterface(comtypes.gen.SAP2000v18.cHelper)
        self._SapObject = self._helper.CreateObject(self.structural.SAP_2000_directory)
        self._SapObject.ApplicationStart(
            Units= 6,
            Visible= False,
            FileName= "")
        self._SapModel = self._SapObject.SapModel
        """
        self.initialize_new_workspace_with_basic_properties()

    def initialize_new_workspace_with_basic_properties(self):
        Units = 6
        self.new_model = self._SapModel.InitializeNewModel(6)
        self.new_file = self._SapModel.File.NewBlank()
        self.material_definition_steel("reflector")
        self.material_definition_steel("tension_ring")
        self.pipe_cross_section_definition("reflector")
        self.pipe_cross_section_definition("tension_ring")

    def material_definition_steel(self, part_of_structure_as_string):
        if part_of_structure_as_string == "reflector":
            material_name = "Steel_S"+str(self.structural.reflector_yielding_point/1000)+"SpaceFrameBars"
            yielding_point = self.structural.reflector_yielding_point
            ultimate_point = self.structural.reflector_ultimate_point
            e_modul = self.structural.reflector_material_e_modul
            specific_weight = self.structural.reflector_material_specific_weight
        elif part_of_structure_as_string == "tension_ring":
            material_name = "Steel_S"+str(self.structural.tension_ring_yielding_point/1000)+"TensionRingBars"
            yielding_point = self.structural.tension_ring_yielding_point
            ultimate_point = self.structural.tension_ring_ultimate_point
            e_modul = self.structural.tension_ring_material_e_modul
            specific_weight = self.structural.tension_ring_material_specific_weight
        self._SapModel.PropMaterial.SetMaterial(
            Name= material_name,
            MatType= 1,
            Color= -1,
            Notes= "custom-made")
        self._SapModel.PropMaterial.SetMPIsotropic(
            Name= material_name,
            E= e_modul,
            U= 0.3,
            A= 1.170e-05)
        self._SapModel.PropMaterial.SetOSteel_1(
            Name= material_name,
            FY= yielding_point,
            Fu= ultimate_point,
            EFy= yielding_point, #effective yield strength
            EFu= ultimate_point, #effective ultimate strength
            SSType= 1, #Stress-Strain curve type. 1 if Parametric-Simple, 0 if User-defined
            SSHysType= 2, #Stress-Strain hysteresis type. 0 Elastic, 1 Kinematic, 2 Takeda
            StrainAtHardening= 0.02, #Applies only for parametric Stress-Strain curves, value of SSType 0.
            StrainAtMaxStress= 0.1, #Applies only for parametric Stress-Strain curves, value of SSType 0.
            StrainAtRupture= 0.2, #Applies only for parametric Stress-Strain curves, value of SSType 0.
            FinalSlope= -0.1, #Applies only for parametric Stress-Strain curves, value of SSType 0.
            Temp= 25) #
        self._SapModel.PropMaterial.SetWeightAndMass(
            Name= material_name,
            MyOption= 1,
            Value= specific_weight)

    def pipe_cross_section_definition(self, part_of_structure_as_string):
        if part_of_structure_as_string == "reflector":
            property_name= "ROR_"+str(1000 * self.structural.reflector_bar_outer_diameter)+"x"+str(1000 * self.structural.reflector_bar_thickness)+"SpaceFrameBars"
            material_name= "Steel_S"+str(self.structural.reflector_yielding_point/1000)+"SpaceFrameBars"
            bar_diameter= self.structural.reflector_bar_outer_diameter
            bar_thickness= self.structural.reflector_bar_thickness
        elif part_of_structure_as_string == "tension_ring":
            property_name = "ROR_"+str(1000 * self.structural.tension_ring_bar_outer_diameter)+"x"+str(1000 * self.structural.tension_ring_bar_thickness)+"TensionRingBars"
            material_name = "Steel_S"+str(self.structural.tension_ring_yielding_point/1000)+"TensionRingBars"
            bar_diameter= self.structural.tension_ring_bar_outer_diameter
            bar_thickness= self.structural.tension_ring_bar_thickness
        self._SapModel.PropFrame.SetPipe(
            Name= property_name,
            MatProp= material_name,
            T3= bar_diameter,
            Tw= bar_thickness,
            Color= -1,
            Notes= "pipe according to SIA263")

    def _shell_definition(self):
        self._SapModel.PropArea.SetShell_1(
            Name= "densless_shell",
            ShellType= 2,
            IncludeDrillingDOF= True,
            MatProp= "Steel_S"+str(self.structural.reflector_yielding_point/1000)+"SpaceFrameBars", #ignored in any case
            MatAng= 0.0,
            Thickness= 0.0,
            Bending= 0.0,
            Color= -1,
            Notes= "surface_included_just_for_wind_load_scenario")

    def _nodes_definition(self, nodes):
        for i in range ((nodes.shape[0])):
            self._SapModel.PointObj.AddCartesian(
                X=nodes[i,0],
                Y=nodes[i,1],
                Z=nodes[i,2],
                Name= 'whatever',
                UserName="node_"+str(i),
                CSys='Global',
                MergeOff=True)

    def _frames_definition(self, bars, part_of_structure_as_string):
        if part_of_structure_as_string == "reflector":
            property_name = "ROR_"+str(1000 * self.structural.reflector_bar_outer_diameter)+"x"+str(1000 * self.structural.reflector_bar_thickness)+"SpaceFrameBars"
        elif part_of_structure_as_string == "tension_ring":
            property_name = "ROR_"+str(1000 * self.structural.tension_ring_bar_outer_diameter)+"x"+str(1000 * self.structural.tension_ring_bar_thickness)+"TensionRingBars"
        for i in range ((bars.shape[0])):
            self._SapModel.FrameObj.AddByPoint(
                Point1="node_"+str(bars[i,0]), #Point name
                Point2="node_"+str(bars[i,1]), #Point name
                PropName= property_name,
                Name='whatever',
                UserName='bar_'+str(i))

    def _set_tension_compression_limits_for_specific_frame_elements(self, cables):
        for i in range(cables.shape[0]):
            self._SapModel.FrameObj.SetTCLimits(
                Name= str(2),
                LimitCompressionExists= True,
                LimitCompression= 0,
                LimitTensionExists= True,
                LimitTension= 100,
                ItemType=0)

    def _cables_definition(self, cables):
        property_name = "Steel_Y"+str(self.structural.cables_yielding_point/1000)+"TensionRingCables"

        self._SapModel.PropMaterial.SetMaterial(
            Name= property_name,
            MatType= 1,
            Color= -1)

        self._SapModel.PropMaterial.SetMPIsotropic(
            Name= property_name,
            E= self.structural.cables_e_modul,
            U= 0.3,
            A= 1.170e-05)

        self._SapModel.PropMaterial.SetOSteel_1(
            Name= property_name,
            FY= self.structural.cables_yielding_point,
            Fu= self.structural.cables_ultimate_point,
            EFy= self.structural.cables_yielding_point, #effective yield strength
            EFu= self.structural.cables_ultimate_point, #effective ultimate strength
            SSType= 1, #Stress-Strain curve type. 1 if Parametric-Simple, 0 if User-defined
            SSHysType= 2, #Stress-Strain hysteresis type. 0 Elastic, 1 Kinematic, 2 Takeda
            StrainAtHardening= 0.02, #Applies only for parametric Stress-Strain curves, value of SSType 0.
            StrainAtMaxStress= 0.1, #Applies only for parametric Stress-Strain curves, value of SSType 0.
            StrainAtRupture= 0.2, #Applies only for parametric Stress-Strain curves, value of SSType 0.
            FinalSlope= -0.1, #Applies only for parametric Stress-Strain curves, value of SSType 0.
            Temp= 25) #

        self._SapModel.PropMaterial.SetWeightAndMass(
            Name= property_name,
            MyOption= 1,
            Value= self.structural.cables_material_specific_weight)

        self._SapModel.PropCable.SetProp(
            Name= property_name,
            MatProp= property_name,
            Area= self.structural.cables_cs_area,
            Color= -1,
            Notes= "steel, flexible, non-free rotating wire ropes with steel core")

        CSarea_mass_weight_modifiers = [1,1,1]
        self._SapModel.PropCable.SetModifiers(
            Name= property_name,
            Value= CSarea_mass_weight_modifiers)

        for i in range(cables.shape[0]):
            self._SapModel.CableObj.AddByPoint(
                Point1= "node_"+str(cables[i,0]),
                Point2= "node_"+str(cables[i,1]),
                Name= "cable_"+str(i),
                PropName= property_name)

    def elastic_support_definition(self, fixtures):
        spring_stiffness= [10e6, 10e6, 10e6, 0, 0, 0]
        for i in range ((fixtures.shape[0])):
            self._SapModel.PointObj.SetSpring("node_"+str(fixtures[i]), spring_stiffness)

    def _restraints_definition(self, fixtures):
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

    def _material_property_modifiers(self, material_name= "densless_shell"):
        stiffness_mass_weight_modifiers= [0,0,0,0,0,0,0,0,0,0]
        self._SapModel.PropArea.SetModifiers(
            Name= material_name,
            Value= stiffness_mass_weight_modifiers)

    def _area_object_with_points_definition(self, mirror_tripods, points_number= 3):
        nodes_of_mirror_tripod= []
        for i in range(len(mirror_tripods)):
            nodes_of_mirror_tripod.append([])
            for j in range(len(mirror_tripods[i])):
                nodes_of_mirror_tripod[i].append("node_"+str(mirror_tripods[i,j]))
            self._SapModel.AreaObj.AddByPoint(
                NumberPoints= points_number,
                Point= nodes_of_mirror_tripod[i],
                Name= "whatever",
                PropName= "densless_shell",
                UserName= "mirror_facet_"+str(i))


    def load_scenario_dead(self, load_pattern_name= "dead_load"):
        self._SapModel.LoadPatterns.Add(
            Name= load_pattern_name,
            MyType= 1,
            SelfWTMultiplier= 1)

    def load_scenario_facet_weight(self, mirror_tripods, load_pattern_name= "facets_live_load"):
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

    def load_scenario_wind(self, mirror_tripods, nodes, load_pattern_name= "wind"):
        self._SapModel.LoadPatterns.Add(
            Name= load_pattern_name,
            MyType= 6,
            SelfWTMultiplier= 0)
        self._shell_definition()
        self._material_property_modifiers()
        self._area_object_with_points_definition(mirror_tripods)
        self._SapModel.LoadPatterns.AutoWind.SetEurocode12005_1(
            Name= load_pattern_name,
            ExposureFrom= 2, #area objects
            DirAngle= self.structural.wind_direction,
            Cpw= 0.0,
            Cpl= 0.0,
            UserZ= True,
            TopZ= np.amax(nodes, axis= 0)[2],
            BottomZ= np.amin(nodes, axis=0)[2]-self.structural.reflector_security_distance_from_ground,
            WindSpeed= self.structural.wind_speed,
            Terrain= self.structural.wind_terrain_factor,
            Orography= self.structural.wind_orography_factor,
            K1= self.structural.wind_K1_factor,
            CsCd= self.structural.wind_CsCd_factor,
            Rho= self.structural.wind_density,
            UserExposure= False)
        self._SapModel.AreaObj.SetLoadWindPressure(
            Name= "ALL",
            LoadPat= "wind",
            MyType= 1,
            cp= self.structural.cpei,
            ItemType= 1)

    def load_combination_3LP_definition(self, structural, CName1= "dead_load", CName2= "facets_live_load", CName3= "wind", load_combination_name= "dead+live+wind"):
        self.load_combination_name = load_combination_name
        self._SapModel.RespCombo.Add(
            Name= load_combination_name,
            ComboType= 0)
        self._SapModel.RespCombo.SetCaseList(load_combination_name, 0, CName1, structural.dead_load_scenario_security_factor)
        self._SapModel.RespCombo.SetCaseList(load_combination_name, 0, CName2, structural.live_load_scenario_security_factor)
        self._SapModel.RespCombo.SetCaseList(load_combination_name, 0, CName3, structural.wind_load_scenario_security_factor)

    def load_combination_2LP_definition(self, structural, CName1= "dead_load", CName2= "facets_live_load", load_combination_name= "dead+live"):
        self.load_combination_name = load_combination_name
        self._SapModel.RespCombo.Add(
            Name= load_combination_name,
            ComboType= 0)
        self._SapModel.RespCombo.SetCaseList(load_combination_name, 0, CName1, structural.dead_load_scenario_security_factor)
        self._SapModel.RespCombo.SetCaseList(load_combination_name, 0, CName2, structural.live_load_scenario_security_factor)

    def non_linearity(self):
        self._SapModel.LoadPatterns.Add("nonlinear_incorporation", 8, 0)
        self._SapModel.LoadCases.StaticNonLinear.SetCase("dead_load")
        self._SapModel.LoadCases.StaticNonLinear.SetCase("facets_live_load")
        self._SapModel.LoadCases.StaticNonLinear.SetCase("nonlinear_incorporation")
        self._SapModel.LoadCases.StaticNonlinear.SetGeometricNonlinearity("dead_load", 2)
        self._SapModel.LoadCases.StaticNonlinear.SetGeometricNonlinearity("facets_live_load", 2)
        self._SapModel.LoadCases.StaticNonlinear.SetGeometricNonlinearity("nonlinear_incorporation", 2)
        self._SapModel.LoadCases.StaticNonLinear.SetLoads("nonlinear_incorporation", 2, ["Load", "Load"], ["dead_load", "facets_live_load"], [1.0, 1.0])
        self._SapModel.RespCombo.Add(Name= "nonlinear_incorporation_combo", ComboType= 0)
        self._SapModel.RespCombo.SetCaseList("nonlinear_incorporation_combo", 0, "nonlinear_incorporation", 1.0)
        self.load_combination_name = "nonlinear_incorporation_combo"

    def non_linearity_wind(self, mirror_tripods, nodes):
        self.load_scenario_wind(mirror_tripods, nodes, load_pattern_name= "wind")
        self._SapModel.LoadCases.StaticNonLinear.SetCase("wind")
        self._SapModel.LoadCases.StaticNonlinear.SetGeometricNonlinearity("wind", 2)
        self._SapModel.LoadCases.StaticNonLinear.SetLoads("wind", 1, ["Load"], ["wind"], [1.0])
        self._SapModel.LoadCases.StaticNonlinear.SetInitialCase("wind", "nonlinear_incorporation")
        self._SapModel.RespCombo.Add(Name= "wind_combo", ComboType= 0)
        self._SapModel.RespCombo.SetCaseList("wind_combo", 0, "wind", 1.0)
        self.load_combination_name = "wind_combo"

    def save_model_in_working_directory(self):
        self._SapModel.File.Save(self.structural.SAP_2000_working_directory)

    def run_analysis(self):
        self._SapModel.Analyze.RunAnalysis()

    def get_displacements_for_group_of_nodes_for_selected_load_pattern(self, load_pattern_name, group_name):
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

    def get_displacements_for_group_of_nodes_for_selected_load_combination(self, load_combination_name, group_name):
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
        Obj, ObjSta, Elm, ElmSta = [], [], [], []
        LoadCase, StepType, StepNum = [], [], []
        P, V2, V3, T, M2, M3 = [], [], [], [], [], []

        [NumberResults, Obj, ObjSta, Elm, ElmSta,
        LoadCase, StepType, StepNum,
        P, V2, V3, T, M2, M3,
        ret] = self._SapModel.Results.FrameForce(
                    Name, ItemTypeElm, NumberResults,
                    Obj, ObjSta, Elm, ElmSta,
                    LoadCase, StepType, StepNum,
                    P, V2, V3, T, M2, M3)
        return forces_arrange(NumberResults, Obj, P, V2, V3, T, M2, M3)

    def get_forces_for_group_of_bars_for_selected_load_combination(self, load_combination_name, dish, part_of_structure):
        if part_of_structure=='reflector':
            self._SapModel.GroupDef.SetGroup(part_of_structure)
            bars=dish['bars_reflector']
            for i in range(bars.shape[0]):
                self._SapModel.FrameObj.SetGroupAssign(
                    Name='bar_'+str(i),
                    GroupName=part_of_structure)
            group_name=part_of_structure
        elif part_of_structure=='tension_ring':
            self._SapModel.GroupDef.SetGroup(part_of_structure)
            bars=dish['bars_tension_ring']
            for i in range(dish['bars_reflector'].shape[0], dish['bars_reflector'].shape[0]+bars.shape[0]):
                self._SapModel.FrameObj.SetGroupAssign(
                    Name='bar_'+str(i),
                    GroupName=part_of_structure)
            group_name=part_of_structure
        elif part_of_structure=='cables':
            self._SapModel.GroupDef.SetGroup(part_of_structure)
            bars=dish['cables']
            for i in range(bars.shape[0]):
                self._SapModel.CableObj.SetGroupAssign(
                    Name='cable_'+str(i),
                    GroupName=part_of_structure)
            group_name=part_of_structure


        self._SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
        self._SapModel.Results.Setup.SetComboSelectedForOutput(load_combination_name)
        Name = group_name
        ItemTypeElm = 2
        NumberResults = 0
        Obj, ObjSta, Elm, ElmSta = [], [], [], []
        LoadCase, StepType, StepNum = [], [], []
        P, V2, V3, T, M2, M3 = [], [], [], [], [], []

        [NumberResults, Obj, ObjSta, Elm, ElmSta,
        LoadCase, StepType, StepNum,
        P, V2, V3, T, M2, M3,
        ret] = self._SapModel.Results.FrameForce(
                    Name, ItemTypeElm, NumberResults,
                    Obj, ObjSta, Elm, ElmSta,
                    LoadCase, StepType, StepNum,
                    P, V2, V3, T, M2, M3)
        return self.forces_arrange(NumberResults, Obj, P, V2, V3, T, M2, M3, part_of_structure)

    def forces_arrange(self, NumberResults, Obj, P, V2, V3, T, M2, M3, part_of_structure):
        forces = []
        for i in range(NumberResults-1):
            if Obj[i] != Obj[i+1]:
                if part_of_structure=="cables":
                    points= self._SapModel.CableObj.GetPoints(Obj[i])
                else:
                    points= self._SapModel.FrameObj.GetPoints(Obj[i])
                coord_1= np.array(self._SapModel.PointObj.GetCoordCartesian(points[0]))
                coord_2= np.array(self._SapModel.PointObj.GetCoordCartesian(points[1]))
                length= np.linalg.norm(coord_1 - coord_2)
                forces.append([Obj[i], length, P[i], V2[i], V3[i], T[i], M2[i], M3[i]])
        if part_of_structure=="cables":
            points= self._SapModel.CableObj.GetPoints(Obj[NumberResults-1])
        else:
            points= self._SapModel.FrameObj.GetPoints(Obj[NumberResults-1])
        coord_1= np.array(self._SapModel.PointObj.GetCoordCartesian(points[0]))
        coord_2= np.array(self._SapModel.PointObj.GetCoordCartesian(points[1]))
        length= np.linalg.norm(coord_1 - coord_2)
        forces.append([Obj[NumberResults-1], length, P[NumberResults-1], V2[NumberResults-1], V3[NumberResults-1], T[NumberResults-1], M2[NumberResults-1], M3[NumberResults-1]])
        return forces

    def get_total_absolute_deformations_for_load_pattern(self, nodes, load_pattern_name, group_name= "ALL"):
        self.group_of_nodes_definition(group_name, flat_part_of_reflector= np.arange(nodes.shape[0]))
        relative_displacements = self.get_displacements_for_group_of_nodes_for_selected_load_pattern(load_pattern_name, group_name)
        nodes_deformed = np.zeros((nodes.shape[0],3))
        for i in range(len(relative_displacements)):
            nodes_deformed[i, 0] = nodes[i, 0] + relative_displacements[i][1]
            nodes_deformed[i, 1] = nodes[i, 1] + relative_displacements[i][2]
            nodes_deformed[i, 2] = nodes[i, 2] + relative_displacements[i][3]
        return nodes_deformed

    def get_total_absolute_deformations_for_load_combination(self, nodes, load_combination_name, group_name= "ALL"):
        self.group_of_nodes_definition(group_name, flat_part_of_reflector= np.arange(nodes.shape[0]))
        relative_displacements = self.get_displacements_for_group_of_nodes_for_selected_load_combination(load_combination_name, group_name)
        nodes_deformed = np.zeros((nodes.shape[0],3))
        for i in range(len(relative_displacements)):
            nodes_deformed[i, 0] = nodes[i, 0] + relative_displacements[i][1]
            nodes_deformed[i, 1] = nodes[i, 1] + relative_displacements[i][2]
            nodes_deformed[i, 2] = nodes[i, 2] + relative_displacements[i][3]
        return nodes_deformed

    def __repr__(self):
        out = "SAP2000_OAPI"
        return out

    def exit_application(self, file_save= "True"):
        self._SapObject.ApplicationExit(file_save)
