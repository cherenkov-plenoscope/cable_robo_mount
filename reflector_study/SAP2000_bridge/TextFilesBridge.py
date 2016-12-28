import numpy as np

class JointsCreate(object):
    def __init__(self, nodes, path):
        self.file_path= path+".$2k"
        self.s2k_contents = self.text_file_to_list(self.file_path)
        self.table_joint_coordinates = self.create_table_nodes(nodes)
        self.final_s2k = self.import_table_to_text_file(self.table_joint_coordinates, self.s2k_contents)
        self.write_contents_to_file(self.final_s2k, self.file_path)

    def text_file_to_list(self, file_path):
        with open(file_path) as f:
            contents = f.readlines()
        return contents

    def create_table_nodes(self, nodes):
        table_joint_coordinates = ["TABLE:  "'"JOINT COORDINATES"'"\n"]
        for i in range(nodes.shape[0]):
            table_joint_coordinates.append("   Joint=node_"+str(i)+"   CoordSys=GLOBAL   CoordType=Cartesian   XorR="+str(nodes[i,0])+"   Y="+str(nodes[i,1])+"   Z="+str(nodes[i,2])+"   SpecialJt=Yes   GUID=e91ddf1b-1450-4830-ae89-2eec09d30794\n")
        table_joint_coordinates.append(" \n")
        return table_joint_coordinates

    def import_table_to_text_file(self, table, s2k_contents):
        final_s2k = s2k_contents[:62] + table + s2k_contents[62:]
        return final_s2k

    def write_contents_to_file(self, contents, path):
        with open(path, "w") as f:
            for item in contents:
                f.write(str(item))

class FramesCreate(object):
    def __init__(self, bars_reflector, bars_tension_ring, structural):
        self.structural = structural
        self.file_path= structural.SAP_2000_working_directory+".$2k"
        self.s2k_contents = self.text_file_to_list(self.file_path)
        self.tables_1_frames, self.tables_2_frames = self.create_table_frames(bars_reflector, bars_tension_ring)
        self.final_s2k_w2 = self.import_table_2_to_text_file(self.tables_2_frames, self.s2k_contents)
        self.final_s2k_w1 = self.import_table_1_to_text_file(self.tables_1_frames, self.final_s2k_w2)
        self.write_contents_to_file(self.final_s2k_w1, self.file_path)

    def text_file_to_list(self, file_path):
        with open(file_path) as f:
            contents = f.readlines()
        return contents

    def create_table_frames(self, bars_reflector, bars_tension_ring):
        bars = np.concatenate((bars_reflector, bars_tension_ring), axis=0)

        tables_1 = ["TABLE:  "'"CONNECTIVITY - FRAME"'"\n"]
        for i in range(bars.shape[0]):
            tables_1.append("   Frame=bar_"+str(i)+"   JointI=node_"+str(bars[i,0])+"   JointJ=node_"+str(bars[i,1])+"   IsCurved=No   GUID=9752f2a1-3a94-4f86-b5ea-81a589ee9daa\n")
        tables_1.append(" \n")

        tables_2 = ["TABLE:  "'"FRAME AUTO MESH ASSIGNMENTS"'"\n"]
        for i in range(bars.shape[0]):
            tables_2.append("   Frame=bar_"+str(i)+"   AutoMesh=Yes   AtJoints=Yes   AtFrames=No   NumSegments=0   MaxLength=0   MaxDegrees=0\n")
        tables_2.append(" \n")
        tables_2.append("TABLE:  "'"FRAME DESIGN PROCEDURES"'"\n")
        for i in range(bars.shape[0]):
            tables_2.append("   Frame=bar_"+str(i)+"   DesignProc="'"From Material"'"\n")
        tables_2.append(" \n")
        tables_2.append("TABLE:  "'"FRAME LOAD TRANSFER OPTIONS"'"\n")
        for i in range(bars.shape[0]):
            tables_2.append("   Frame=bar_"+str(i)+"   Transfer=Yes\n")
        tables_2.append(" \n")
        tables_2.append("TABLE:  "'"FRAME OUTPUT STATION ASSIGNMENTS"'"\n")
        for i in range(bars.shape[0]):
            tables_2.append("   Frame=bar_"+str(i)+"   StationType=MaxStaSpcg   MaxStaSpcg=0.5   AddAtElmInt=Yes   AddAtPtLoad=Yes\n")
        tables_2.append(" \n")
        tables_2.append("TABLE:  "'"FRAME SECTION ASSIGNMENTS"'"\n")
        self.property_name_reflector = "ROR_"+str(1000 * self.structural.reflector_bar_outer_diameter)+"x"+str(1000 * self.structural.reflector_bar_thickness)+"SpaceFrameBars"
        self.property_name_tension_ring = "ROR_"+str(1000 * self.structural.tension_ring_bar_outer_diameter)+"x"+str(1000 * self.structural.tension_ring_bar_thickness)+"TensionRingBars"
        for i in range(bars_reflector.shape[0]):
            tables_2.append("   Frame=bar_"+str(i)+"   AutoSelect=N.A.   AnalSect="+self.property_name_reflector+"   MatProp=Default\n")
        for i in range(bars_tension_ring.shape[0]):
            tables_2.append("   Frame=bar_"+str(bars_reflector.shape[0]+i)+"   AutoSelect=N.A.   AnalSect="+self.property_name_tension_ring+"   MatProp=Default\n")
        tables_2.append(" \n")

        return tables_1, tables_2

    def import_table_1_to_text_file(self, tables_1, s2k_contents):
        final_s2k = s2k_contents[:17] + tables_1 + s2k_contents[17:]
        return final_s2k

    def import_table_2_to_text_file(self, tables_2, s2k_contents):
        final_s2k = s2k_contents[:25] + tables_2 + s2k_contents[25:]
        return final_s2k

    def write_contents_to_file(self, contents, path):
        with open(path, "w") as f:
            for item in contents:
                f.write(str(item))
