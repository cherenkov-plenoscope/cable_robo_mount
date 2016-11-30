import numpy as np

knicken_dict= {
    "wirkend_normalkraft": 19, #in kN
    "geometry": {
        "bar_length": 3000, #in mm
        "knicklaengebeiwert": 0.7, #für einfach gelagert Stab 1, eineitig eingespannt 0.7, beidseitig eingespannt 0.5
        "imperfektionsbeiwert": 0.49},
    "querschnitt": {
        "outer_diameter": 42.4, #in mm
        "thickness": 2.6},
    "material": {
        "elastizitaetsmodul": 210000, #in MPa
        "fliessspannungen": 235, #in MPa
        "sicherheitsfaktor": 1.05}, #unitless
              }

class Knicknachweis(object):

    def __init__(self, knicken_dict):
        self.wirkend_normalkraft = knicken_dict["wirkend_normalkraft"]
        self.bar_length = knicken_dict["geometry"]["bar_length"]
        self.knicklaengebeiwert = knicken_dict["geometry"]["knicklaengebeiwert"]
        self.imperfektionsbeiwert = knicken_dict["geometry"]["imperfektionsbeiwert"]
        self.bar_outer_diameter = knicken_dict["querschnitt"]["outer_diameter"]
        self.bar_thickness = knicken_dict["querschnitt"]["thickness"]
        self.elastizitaetsmodul = knicken_dict["material"]["elastizitaetsmodul"]
        self.fliessspannungen = knicken_dict["material"]["fliessspannungen"]
        self.sicherheitsfaktor = knicken_dict["material"]["sicherheitsfaktor"]
        self._set_up_querschnittswerte_and_geometry()
        self._set_up_necessary_factors()
        self.normalkraftwiderstand = self._normalkraftwiderstand(self.fliessspannungen, self.profilflaeche, self.sicherheitsfaktor)
        self.knickwiderstand = self._knickwiderstand(self.normalkraftwiderstand, self.abminderungsfaktor)
        if self.wirkend_normalkraft <= self.knickwiderstand/1000:
            print("Nachweis erfüllt.")
        else:
            print("Nachweis nicht erfüllt.")

    def _set_up_querschnittswerte_and_geometry(self):
        self.profilflaeche = np.pi*(self.bar_outer_diameter**2/4-(self.bar_outer_diameter-2*self.bar_thickness)**2/4)
        self.traegheitsmoment = np.pi*((self.bar_outer_diameter/2)**4-((self.bar_outer_diameter-2*self.bar_thickness)/2)**4)/4
        self.knicklaenge = self.bar_length*self.knicklaengebeiwert

    def _set_up_necessary_factors(self):
        self.fliessschlankheit = self._fliessschlankheit(self.fliessspannungen, self.elastizitaetsmodul)
        self.stabschlankheit = self._stabschlankheit(self.knicklaenge, self.profilflaeche, self.traegheitsmoment)
        self.bezogene_schlankheit = self._bezogene_schlankheit(self.fliessschlankheit, self.stabschlankheit)
        self.abminderungsfaktor = self._abminderungsfaktor(self.imperfektionsbeiwert, self.bezogene_schlankheit)



    def _fliessschlankheit(self, fliessspannungen, elastizitaetsmodul):
        """
        Returns the Fliessschlankheit in (-)

        parameter
        ---------
            elastizitaetsmodul    E-Modul von Stahl in MPa. (gemäss SIA263 210000MPa)

            fliessspannungen      Die maxmimal erreichbare Fliessspanungen in MPa. (z.B. für S235 Stahl 235MPa)
        """
        return np.pi*np.sqrt(elastizitaetsmodul/fliessspannungen)

    def _stabschlankheit(self, knicklaenge, profilflaeche, traegheitsmoment):
        """
        Returns the Stabschlankheit (-)

        parameter
        ---------
            knicklaenge         Der Knicklänge des Stabes in mm.

            profilflaeche       Die Profifläche in mm**2.

            traegheitsmoment    Der Profilträgheitsmoment in mm**4.
        """
        return knicklaenge*np.sqrt(profilflaeche/traegheitsmoment)

    def _bezogene_schlankheit(self, fliessschlankheit, stabschlankheit):
        """
        Returns the bezogene Schlankheit in (-)

        parameter
        ---------
            fliessschlankheit     Die Fliessschlankheit in (-).

            Stabschlankheit       Die Stabschlankheit in (-).
        """
        return stabschlankheit/fliessschlankheit

    def _abminderungsfaktor(self, imperfektionsbeiwert, bezogene_schlankheit):
        """
        Returns the Abminderungsfaktor in (-)

        parameter
        ---------
            imperfektionsbeiwert       Der Imperfektionsbeiwert a_k in (-). Gemäss SIA263 Tabelle 8, a_k= 0.21, 0.34, 0.49, 0.76 für Knickspannungskurve a, b, c, d entsprechend.

            bezogene_schlankheit       Die bezogene Schlankheit in (-).
        """
        fi_k= 0.5*(1+imperfektionsbeiwert*(bezogene_schlankheit-0.2)+bezogene_schlankheit**2)
        xi_k= 1/(fi_k+np.sqrt(fi_k**2-bezogene_schlankheit**2))
        if xi_k > 1:
            xi_k= 1.0
        return xi_k

    def _normalkraftwiderstand(self, fliessspannungen, profilflaeche, sicherheitsfaktor):
        """
        Returns the Normalkraftwiderstand in N (elastisch=plastisch)

        parameter
        ---------
            fliessspannungen        Die maxmimal erreichbare Fliessspanungen in MPa.

            profilflaeche           Die Profifläche in mm**2.

            sicherheitsfaktor       Der Sicherheitsfaktor in (-). Gemäss SIA263 Ziffer 4.1.3 gama_mi_1= 1.05.
        """
        return fliessspannungen*profilflaeche/sicherheitsfaktor

    def _knickwiderstand(self, normalkraftwiderstand, abminderungsfaktor):
        """
        Returns the Knickwiderstand in N

        parameter
        ---------
            normalkraftwiderstand        Der Normalkraftwiderstand des Querschnitts in N.

            abminderungsfaktor           Der Abminderungsfaktor in (-).
        """
        return normalkraftwiderstand*abminderungsfaktor
