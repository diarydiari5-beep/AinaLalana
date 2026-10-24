class Lieu:
    def __init__(self, id_lieu=None, nom_lieu="", type_lieu="village", lits_dispo=None, medecin_present=None, derniere_maj=None):
        self._id_lieu = id_lieu
        self._nom_lieu = nom_lieu
        self._type_lieu = type_lieu
        self._lits_disponibles = lits_dispo
        self._medecin_present = medecin_present
        self._derniere_mise_a_jour = derniere_maj

    # Getters
    def _get_id_lieu(self): return self._id_lieu
    def _get_nom_lieu(self): return self._nom_lieu
    def _get_type_lieu(self): return self._type_lieu
    def _get_lits_disponibles(self): return self._lits_disponibles
    def _get_medecin_present(self): return self._medecin_present
    def _get_derniere_mise_a_jour(self): return self._derniere_mise_a_jour

    # Setters
    def _set_id_lieu(self, v): self._id_lieu = v
    def _set_nom_lieu(self, v): self._nom_lieu = v
    def _set_type_lieu(self, v): self._type_lieu = v
    def _set_lits_disponibles(self, v):
        if self._type_lieu == 'csb' and (v is None or v >= 0):
            self._lits_disponibles = v
    def _set_medecin_present(self, v): self._medecin_present = v
    def _set_derniere_mise_a_jour(self, v): self._derniere_mise_a_jour = v

    # Propriétés
    id_lieu = property(_get_id_lieu, _set_id_lieu)
    nom_lieu = property(_get_nom_lieu, _set_nom_lieu)
    type_lieu = property(_get_type_lieu, _set_type_lieu)
    lits_disponibles = property(_get_lits_disponibles, _set_lits_disponibles)
    medecin_present = property(_get_medecin_present, _set_medecin_present)
    derniere_mise_a_jour = property(_get_derniere_mise_a_jour, _set_derniere_mise_a_jour)