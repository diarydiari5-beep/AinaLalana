import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.services.service_csb import ServiceCSB
from backend.services.service_routage import ServiceRoutage
from backend.services.service_signalement import ServiceSignalement
from backend.services.service_auth import ServiceAuth

journal_ctrl = logging.getLogger("journal_controleur_gestionnaire")


class ControleurGestionnaire:
    def __init__(self):
        self._service_csb = ServiceCSB()
        self._service_routage = ServiceRoutage()
        self._service_signalement = ServiceSignalement()
        self._service_auth = ServiceAuth()

    def _id_csb_assigne(self) -> str | None:
        session = self._service_auth.obtenir_session()
        if not session or session.get("role") != "gestionnaire_csb":
            return None
        id_csb = session.get("id_csb")
        return str(id_csb) if id_csb else None

    def consulter_csb(self, id_csb: str = None) -> dict:
        id_assigne = self._id_csb_assigne()
        if id_assigne is not None:
            if not id_assigne:
                return {"succes": True, "csb": [], "total": 0}
            csb = self._service_csb.obtenir_csb_par_id(id_assigne)
            if not csb:
                return {"succes": True, "csb": [], "total": 0}
            return {"succes": True, "csb": [csb], "total": 1}
        if id_csb:
            csb = self._service_csb.obtenir_csb_par_id(id_csb)
            if not csb:
                return {"succes": False, "message": "CSB introuvable."}
            return {"succes": True, "csb": [csb], "total": 1}
        tous = self._service_csb.obtenir_tous_csb()
        return {"succes": True, "csb": tous, "total": len(tous)}

    def mettre_a_jour_csb(
        self, id_csb: str, lits: int = None, medecin: bool = None
    ) -> dict:
        if not id_csb:
            return {"succes": False, "message": "ID du CSB requis."}
        id_assigne = self._id_csb_assigne()
        if id_assigne is not None:
            if not id_assigne:
                return {"succes": False, "message": "Aucun CSB associé à votre compte."}
            if str(id_csb) != id_assigne:
                return {
                    "succes": False,
                    "message": "Vous ne pouvez modifier que votre CSB assigné.",
                }
        ok = self._service_csb.mettre_a_jour_csb(id_csb, lits, medecin)
        if ok:
            return {"succes": True, "message": "CSB mis à jour avec succès."}
        return {"succes": False, "message": "Échec de la mise à jour du CSB."}

    def consulter_routes(self) -> dict:
        routes = self._service_routage.obtenir_toutes_routes()
        return {"succes": True, "routes": routes, "total": len(routes)}

    def maj_etat_route(self, id_route: int, nouvel_etat: str) -> dict:
        if nouvel_etat not in ("praticable", "difficile", "coupee"):
            return {"succes": False, "message": "État invalide."}
        self._service_signalement.appliquer_signalement_route(
            id_route, nouvel_etat, self._service_routage
        )
        return {"succes": True, "message": "État de la route mis à jour."}
