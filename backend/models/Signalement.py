class Signalement:
    def __init__(self, id_signalement=None, id_utilisateur=None, id_route=None, etat_signale="", date_signalement=None, commentaire=""):
        self._id_signalement = id_signalement
        self._id_utilisateur = id_utilisateur
        self._id_route = id_route
        self._etat_signale = etat_signale
        self._date_signalement = date_signalement
        self._commentaire = commentaire

    # Getters
    def _get_id_signalement(self): return self._id_signalement
    def _get_id_utilisateur(self): return self._id_utilisateur
    def _get_id_route(self): return self._id_route
    def _get_etat_signale(self): return self._etat_signale
    def _get_date_signalement(self): return self._date_signalement
    def _get_commentaire(self): return self._commentaire

    # Setters
    def _set_id_signalement(self, v): self._id_signalement = v
    def _set_id_utilisateur(self, v): self._id_utilisateur = v
    def _set_id_route(self, v): self._id_route = v
    def _set_etat_signale(self, v): self._etat_signale = v
    def _set_date_signalement(self, v): self._date_signalement = v
    def _set_commentaire(self, v): self._commentaire = v

    # Propriétés
    id_signalement = property(_get_id_signalement, _set_id_signalement)
    id_utilisateur = property(_get_id_utilisateur, _set_id_utilisateur)
    id_route = property(_get_id_route, _set_id_route)
    etat_signale = property(_get_etat_signale, _set_etat_signale)
    date_signalement = property(_get_date_signalement, _set_date_signalement)
    commentaire = property(_get_commentaire, _set_commentaire)