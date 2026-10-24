class Route:
    def __init__(self, id_route=None, id_depart=None, id_arrivee=None, distance=0.0, etat="praticable"):
        self._id_route = id_route
        self._id_lieu_depart = id_depart
        self._id_lieu_arrivee = id_arrivee
        self._distance_km = float(distance) if distance is not None else None
        self._etat = etat

    def _get_id_route(self): return self._id_route
    def _get_id_lieu_depart(self): return self._id_lieu_depart
    def _get_id_lieu_arrivee(self): return self._id_lieu_arrivee
    def _get_distance_km(self): return self._distance_km
    def _get_etat(self): return self._etat
    
    # Getter spécifique pour Dijkstra pas de setter car c'est une valeur calculé
    def _get_poids(self):
        if self._etat == 'coupee': return float('inf')
        if self._etat == 'difficile': return self._distance_km * 2.0
        return self._distance_km

    def _set_id_route(self, v): self._id_route = v
    def _set_id_lieu_depart(self, v): self._id_lieu_depart = v
    def _set_id_lieu_arrivee(self, v): self._id_lieu_arrivee = v
    def _set_distance_km(self, v): self._distance_km = float(v) if v is not None else None
    def _set_etat(self, v):
        if v in ['praticable', 'difficile', 'coupee']:
            self._etat = v

    id_route = property(_get_id_route, _set_id_route)
    id_lieu_depart = property(_get_id_lieu_depart, _set_id_lieu_depart)
    id_lieu_arrivee = property(_get_id_lieu_arrivee, _set_id_lieu_arrivee)
    distance_km = property(_get_distance_km, _set_distance_km)
    etat = property(_get_etat, _set_etat)
    poids = property(_get_poids) # Propriété en lecture seule