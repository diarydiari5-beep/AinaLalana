class Itineraire:
    def __init__(self, id_itineraire=None, id_user=None, id_depart=None, id_csb=None, distance=0.0, algorithme="dijkstra", date_calcul=None, notification=""):
        self._id_itineraire = id_itineraire
        self._id_utilisateur = id_user
        self._id_lieu_depart = id_depart
        self._id_csb_recommande = id_csb
        self._distance_totale_km = distance
        self._algorithme = algorithme
        self._date_calcul = date_calcul
        self._notification = notification
        self._etapes = []

    # Getters
    def _get_id_itineraire(self): return self._id_itineraire
    def _get_id_utilisateur(self): return self._id_utilisateur
    def _get_id_lieu_depart(self): return self._id_lieu_depart
    def _get_id_csb_recommande(self): return self._id_csb_recommande
    def _get_distance_totale_km(self): return self._distance_totale_km
    def _get_algorithme(self): return self._algorithme
    def _get_date_calcul(self): return self._date_calcul
    def _get_notification(self): return self._notification
    def _get_etapes(self): return self._etapes

    # Setters
    def _set_id_itineraire(self, v): self._id_itineraire = v
    def _set_id_utilisateur(self, v): self._id_utilisateur = v
    def _set_id_lieu_depart(self, v): self._id_lieu_depart = v
    def _set_id_csb_recommande(self, v): self._id_csb_recommande = v
    def _set_distance_totale_km(self, v): self._distance_totale_km = v
    def _set_algorithme(self, v): self._algorithme = v
    def _set_date_calcul(self, v): self._date_calcul = v
    def _set_notification(self, v): self._notification = v
    def _set_etapes(self, v): self._etapes = v

    # Propriétés
    id_itineraire = property(_get_id_itineraire, _set_id_itineraire)
    id_utilisateur = property(_get_id_utilisateur, _set_id_utilisateur)
    id_lieu_depart = property(_get_id_lieu_depart, _set_id_lieu_depart)
    id_csb_recommande = property(_get_id_csb_recommande, _set_id_csb_recommande)
    distance_totale_km = property(_get_distance_totale_km, _set_distance_totale_km)
    algorithme = property(_get_algorithme, _set_algorithme)
    date_calcul = property(_get_date_calcul, _set_date_calcul)
    notification = property(_get_notification, _set_notification)
    etapes = property(_get_etapes, _set_etapes)