import numpy as np

class Knicknachweis(object):

    def __init__(self, config_dict, forces):
        self.forces = forces
        self.buckling_length_factor = config_dict["reflector"]["bars"]["buckling_length_factor"]
        self.imperfection_factor = config_dict["reflector"]["bars"]["imperfection_factor"]
        self.bar_outer_diameter = config_dict["reflector"]["bars"]["outer_diameter"]
        self.bar_thickness = config_dict["reflector"]["bars"]["thickness"]
        self.e_modul = config_dict["reflector"]["material"]["e_modul"]
        self.yielding_point = config_dict["reflector"]["material"]["yielding_point"]
        self.security_factor = config_dict["reflector"]["material"]["security_factor"]

        self._set_up_material_and_cross_section_factors()

        self.log = []
        for i in range(len(forces)):
            bar_id= self.forces[i][0]
            bar_length= self.forces[i][1]
            axial_force= self.forces[i][2]
            max_shear= max(abs(self.forces[i][3]), abs(self.forces[i][4]))
            max_moment= max(abs(self.forces[i][5]), abs(self.forces[i][6]), abs(self.forces[i][7]))
            self.buckling_length = bar_length*self.buckling_length_factor
            self.stabschlankheit = self._stabschlankheit(self.buckling_length, self.profil_area, self.moment_of_inertia)
            self.bezogene_schlankheit = self._bezogene_schlankheit(self.fliessschlankheit, self.stabschlankheit)
            self.abminderungsfaktor = self._abminderungsfaktor(self.imperfection_factor, self.bezogene_schlankheit)

            self.normalkraftwiderstand = self._normalkraftwiderstand(self.yielding_point, self.profil_area, self.security_factor)
            self.knickwiderstand = self._knickwiderstand(self.normalkraftwiderstand, self.abminderungsfaktor)

            if axial_force <= self.knickwiderstand:
                self.log.append([bar_id, "Nachweis erfüllt.", "Ratio_to_axial_resistance="+str(axial_force/self.knickwiderstand), "Ratio_axial_force_to_max_moment="+str(max_moment/axial_force), "Ratio_axial_force_to_max_shear="+str(max_shear/axial_force)])
            else:
                self.log.append([bar_id, "Nachweis nicht erfüllt.", "Ratio_to_axial_resistance="+str(axial_force/self.knickwiderstand), "Ratio_axial_force_to_max_moment="+str(max_moment/axial_force), "Ratio_axial_force_to_max_shear="+str(max_shear/axial_force)])
        message = "Nachweis nicht erfüllt."
        if message in self.log:
            print("Ultimate limit state exceeded")
        else:
            print("Ultimate limit state not exceeded")

    def _set_up_material_and_cross_section_factors(self):
        self.profil_area = np.pi*(self.bar_outer_diameter**2/4-(self.bar_outer_diameter-2*self.bar_thickness)**2/4)
        self.moment_of_inertia = np.pi*((self.bar_outer_diameter/2)**4-((self.bar_outer_diameter-2*self.bar_thickness)/2)**4)/4
        self.fliessschlankheit = self._fliessschlankheit(self.yielding_point, self.e_modul)

    def _fliessschlankheit(self, yielding_point, e_modul):
        """
        Returns the Fliessschlankheit in (-)

        parameter
        ---------
            e_modul    E-Modul von Stahl in MPa. (gemäss SIA263 210000MPa)

            yielding_point      Die maxmimal erreichbare Fliessspanungen in MPa. (z.B. für S235 Stahl 235MPa)
        """
        return np.pi*np.sqrt(e_modul/yielding_point)

    def _stabschlankheit(self, buckling_length, profil_area, moment_of_inertia):
        """
        Returns the Stabschlankheit (-)

        parameter
        ---------
            buckling_length         Der Knicklänge des Stabes in mm.

            profil_area       Die Profifläche in mm**2.

            moment_of_inertia    Der Profilträgheitsmoment in mm**4.
        """
        return buckling_length*np.sqrt(profil_area/moment_of_inertia)

    def _bezogene_schlankheit(self, fliessschlankheit, stabschlankheit):
        """
        Returns the bezogene Schlankheit in (-)

        parameter
        ---------
            fliessschlankheit     Die Fliessschlankheit in (-).

            Stabschlankheit       Die Stabschlankheit in (-).
        """
        return stabschlankheit/fliessschlankheit

    def _abminderungsfaktor(self, imperfection_factor, bezogene_schlankheit):
        """
        Returns the Abminderungsfaktor in (-)

        parameter
        ---------
            imperfection_factor       Der Imperfektionsbeiwert a_k in (-). Gemäss SIA263 Tabelle 8, a_k= 0.21, 0.34, 0.49, 0.76 für Knickspannungskurve a, b, c, d entsprechend.

            bezogene_schlankheit       Die bezogene Schlankheit in (-).
        """
        fi_k= 0.5*(1+imperfection_factor*(bezogene_schlankheit-0.2)+bezogene_schlankheit**2)
        xi_k= 1/(fi_k+np.sqrt(fi_k**2-bezogene_schlankheit**2))
        if xi_k > 1:
            xi_k= 1.0
        return xi_k

    def _normalkraftwiderstand(self, yielding_point, profil_area, security_factor):
        """
        Returns the Normalkraftwiderstand in N (elastisch=plastisch)

        parameter
        ---------
            yielding_point        Die maxmimal erreichbare Fliessspanungen in MPa.

            profil_area           Die Profifläche in mm**2.

            security_factor       Der Sicherheitsfaktor in (-). Gemäss SIA263 Ziffer 4.1.3 gama_mi_1= 1.05.
        """
        return yielding_point*profil_area/security_factor

    def _knickwiderstand(self, normalkraftwiderstand, abminderungsfaktor):
        """
        Returns the Knickwiderstand in N

        parameter
        ---------
            normalkraftwiderstand        Der Normalkraftwiderstand des Querschnitts in N.

            abminderungsfaktor           Der Abminderungsfaktor in (-).
        """
        return normalkraftwiderstand*abminderungsfaktor
