class EtapeItineraire:
    def __init__(self, id_etape=None, id_itineraire=None, id_lieu=None, ordre=0):
        self._id_etape = id_etape
        self._id_itineraire = id_itineraire
        self._id_lieu = id_lieu
        self._ordre = ordre

    # Getters
    def _get_id_etape(self): return self._id_etape
    def _get_id_itineraire(self): return self._id_itineraire
    def _get_id_lieu(self): return self._id_lieu
    def _get_ordre(self): return self._ordre

    # Setters
    def _set_id_etape(self, v): self._id_etape = v
    def _set_id_itineraire(self, v): self._id_itineraire = v
    def _set_id_lieu(self, v): self._id_lieu = v
    def _set_ordre(self, v): self._ordre = v

    # Propriétés
    id_etape = property(_get_id_etape, _set_id_etape)
    id_itineraire = property(_get_id_itineraire, _set_id_itineraire)
    id_lieu = property(_get_id_lieu, _set_id_lieu)
    ordre = property(_get_ordre, _set_ordre)