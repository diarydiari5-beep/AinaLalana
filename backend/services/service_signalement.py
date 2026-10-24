import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from database.DAO.SignalementDAO import SignalementDAO
from database.DAO.RouteDAO import RouteDAO

journal_signalement = logging.getLogger("journal_signalement")


class ServiceSignalement:
    def __init__(self):
        self._signalement_dao = SignalementDAO()
        self._route_dao = RouteDAO()

    def signaler_route(
        self,
        id_utilisateur: int,
        id_route: int,
        etat_signale: str,
        commentaire: str = "",
    ) -> bool:
        if etat_signale not in ("praticable", "difficile", "coupee"):
            journal_signalement.warning(
                "État invalide: %s. Utiliser praticable, difficile ou coupee.",
                etat_signale,
            )
            return False
        try:
            self._signalement_dao.creer(
                id_utilisateur, id_route, etat_signale, commentaire
            )
            journal_signalement.info(
                "Signalement créé: user=%s, route=%s, etat=%s",
                id_utilisateur,
                id_route,
                etat_signale,
            )
            return True
        except Exception as exc:
            journal_signalement.error("Erreur création signalement: %s", exc)
            return False

    def enregistrer_signalement_citoyen(
        self,
        id_utilisateur: int,
        id_route: int,
        etat_signale: str,
        commentaire: str,
        service_routage,
    ) -> bool:
        """
        Enregistre un signalement citoyen.
        Les états difficile/coupée sont appliqués tout de suite ;
        praticable (réouverture) attend la validation admin (bouton Résolu).
        """
        ok = self.signaler_route(
            id_utilisateur, id_route, etat_signale, commentaire
        )
        if ok and etat_signale != "praticable":
            self.appliquer_signalement_route(
                id_route, etat_signale, service_routage
            )
        return ok

    def appliquer_signalement_route(
        self, id_route: int, nouvel_etat: str, service_routage
    ) -> bool:
        if nouvel_etat not in ("praticable", "difficile", "coupee"):
            return False
        try:
            self._route_dao.update_etat(id_route, nouvel_etat)
            service_routage.appliquer_signalement(id_route, nouvel_etat)
            journal_signalement.info(
                "Route %s → %s appliqué au graphe.", id_route, nouvel_etat
            )
            return True
        except Exception as exc:
            journal_signalement.error(
                "Erreur application signalement route %s: %s", id_route, exc
            )
            return False
