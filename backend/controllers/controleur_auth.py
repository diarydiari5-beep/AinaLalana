import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.services.service_auth import ServiceAuth

journal_ctrl = logging.getLogger("journal_controleur_auth")


class ControleurAuth:
    def __init__(self):
        self._service_auth = ServiceAuth()

    def connexion(self, email: str, mdp: str) -> dict:
        if not email or not mdp:
            return {"succes": False, "message": "Email et mot de passe requis."}
        session = self._service_auth.authentifier(email, mdp)
        if session:
            message = (
                f"Bienvenue {session['prenom']} {session['nom']} "
                f"(rôle: {session['role']})"
            )
            journal_ctrl.info("Connexion réussie: %s", email)
            return {
                "succes": True,
                "message": message,
                "utilisateur": session,
            }
        return {"succes": False, "message": "Email ou mot de passe incorrect."}

    def deconnexion(self) -> dict:
        self._service_auth.deconnecter()
        return {"succes": True, "message": "Déconnexion réussie."}

    def session_active(self) -> dict:
        session = self._service_auth.obtenir_session()
        if session:
            return {"connecte": True, "utilisateur": session}
        return {"connecte": False, "utilisateur": None}

    def verifier_role(self, role: str) -> dict:
        autorise = self._service_auth.verifier_role(role)
        return {"autorise": autorise, "role_requis": role}
