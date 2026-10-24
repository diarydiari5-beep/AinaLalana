class Utilisateur:
    def __init__(self, id_utilisateur=None, nom="", prenom="", email="", mdp="", role="citoyen", actif=True, id_csb=None):
        self._id_utilisateur = id_utilisateur
        self._nom = nom
        self._prenom = prenom
        self._email = email
        self._mdp = mdp
        self._role = role
        self._actif = actif
        self._id_csb = id_csb

    # Getters
    def _get_id_utilisateur(self): return self._id_utilisateur
    def _get_nom(self): return self._nom
    def _get_prenom(self): return self._prenom
    def _get_email(self): return self._email
    def _get_mdp(self): return self._mdp
    def _get_role(self): return self._role
    def _get_actif(self): return self._actif
    def _get_id_csb(self): return self._id_csb

    # Setters
    def _set_id_utilisateur(self, v): self._id_utilisateur = v
    def _set_nom(self, v): self._nom = v
    def _set_prenom(self, v): self._prenom = v
    def _set_email(self, v): self._email = v
    def _set_mdp(self, v): self._mdp = v
    def _set_role(self, v):
        if v in ['citoyen', 'gestionnaire_csb', 'chef_district']:
            self._role = v
    def _set_actif(self, v): self._actif = v
    def _set_id_csb(self, v): self._id_csb = v

    # Propriétés
    id_utilisateur = property(_get_id_utilisateur, _set_id_utilisateur)
    nom = property(_get_nom, _set_nom)
    prenom = property(_get_prenom, _set_prenom)
    email = property(_get_email, _set_email)
    mdp = property(_get_mdp, _set_mdp)
    role = property(_get_role, _set_role)
    actif = property(_get_actif, _set_actif)
    id_csb = property(_get_id_csb, _set_id_csb)