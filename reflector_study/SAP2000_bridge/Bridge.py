import os
import sys
import comtypes.client
import numpy as np


class Bridge(object):

    def __init__(self, config_dict):
        self._SAP2000_directory = config_dict["SAP_2000_directory"]
        self._yielding_point = config_dict["material"]["yielding_point"]
        self._ultimate_point = config_dict["material"]["ultimate_point"]
        self._outter_radius = config_dict["bar_properties"]["outter_radius"]
        self._thickness = config_dict["bar_properties"]["thickness"]
        self._execute_SAP2000()

    def _execute_SAP2000(self):
        self._helper = comtypes.client.CreateObject("Sap2000v18.Helper").QueryInterface(comtypes.gen.SAP2000v18.cHelper)
        self._SapObject = self._helper.CreateObject(self._SAP2000_directory)
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
            Name= "Steel_S"+str(self._yielding_point/1000), #Divided by 1000 cause we give it in kPa. Notation is in MPa.
            MatType= steel,
            Color= -1,
            Notes= "custom-made")
        self._SapModel.PropMaterial.SetOSteel_1(
            Name= "Steel_S"+str(self._yielding_point/1000), #Divided by 1000 cause we give it in kPa. Notation is in MPa.
            FY= self._yielding_point,
            Fu= self._ultimate_point,
            EFy= self._yielding_point, #effective yield strength
            EFu= self._ultimate_point, #effective ultimate strength
            SSType= 1, #Stress-Strain curve type. 1 if Parametric-Simple, 0 if User-defined
            SSHysType= 2, #Stress-Strain hysteresis type. 0 Elastic, 1 Kinematic, 2 Takeda
            StrainAtHardening= 0.02, #Applies only for parametric Stress-Strain curves, value of SSType 0.
            StrainAtMaxStress= 0.1, #Applies only for parametric Stress-Strain curves, value of SSType 0.
            StrainAtRupture= 0.2, #Applies only for parametric Stress-Strain curves, value of SSType 0.
            FinalSlope= -0.1, #Applies only for parametric Stress-Strain curves, value of SSType 0.
            Temp= 25) #

    def cross_section_definition(self):
        self._SapModel.PropFrame.SetPipe(
            Name= "ROR_"+str(1000 * self._outter_radius)+"x"+str(1000 * self._thickness),
            MatProp= "Steel_S"+str(self._yielding_point/1000),
            T3= self._outter_radius,
            Tw= self._thickness,
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
                PropName="ROR_"+str(1000 * self._outter_radius)+"x"+str(1000 * self._thickness),
                Name='whatever',
                UserName='bar_'+str(i))

    def restraints_definition(self, reflector):
        fixtures = reflector["fixtures"]
        deegres_of_freedom = [True, True, True, True, True, True]
        for i in range ((fixtures.shape[0])):
            self._SapModel.PointObj.SetRestraint(
                Name= "node_"+str(fixtures[i]), 
                Value= deegres_of_freedom,
                ItemType= 0)
