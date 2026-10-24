import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from database.DAO.UtilisateurDAO import UtilisateurDAO
from backend.models.Utilisateur import Utilisateur

journal_auth = logging.getLogger("journal_auth")

ROLES_AUTORISES = ("citoyen", "gestionnaire_csb", "chef_district")


class ServiceAuth:
    def __init__(self):
        self._utilisateur_dao = UtilisateurDAO()
        self._session: dict | None = None

    def authentifier(self, email: str, mdp: str) -> dict | None:
        if not email or not mdp:
            return None
        try:
            user = self._utilisateur_dao.verifier_connexion(email, mdp)
            if user:
                self._session = {
                    "id_utilisateur": user["id_utilisateur"],
                    "nom": user["nom"],
                    "prenom": user["prenom"],
                    "email": user["email"],
                    "role": user["role"],
                    "id_csb": user.get("id_csb"),
                }
                journal_auth.info(
                    "Authentification réussie: %s %s (%s)",
                    user["prenom"],
                    user["nom"],
                    user["role"],
                )
                return self._session
            journal_auth.warning(
                "Échec authentification pour %s: identifiants invalides.", email
            )
            return None
        except Exception as exc:
            journal_auth.error("Erreur authentification: %s", exc)
            return None

    def obtenir_session(self) -> dict | None:
        return self._session

    def deconnecter(self):
        self._session = None
        journal_auth.info("Utilisateur déconnecté.")

    def est_connecte(self) -> bool:
        return self._session is not None

    def verifier_role(self, role_requis: str) -> bool:
        if not self._session:
            return False
        if role_requis not in ROLES_AUTORISES:
            return False
        return self._session["role"] == role_requis

    def verifier_un_role(self, roles: list[str]) -> bool:
        if not self._session:
            return False
        return self._session["role"] in roles
