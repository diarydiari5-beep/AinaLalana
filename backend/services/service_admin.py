import logging
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from database.DAO.lieuDAO import LieuDAO
from database.DAO.RouteDAO import RouteDAO

journal_admin = logging.getLogger("journal_admin")


class ServiceAdmin:
    def __init__(self):
        self._lieu_dao = LieuDAO()
        self._route_dao = RouteDAO()

    def obtenir_statistiques(self) -> dict:
        try:
            lieux = self._lieu_dao.get_all()
            routes = self._route_dao.get_all()

            total_villages = sum(1 for l in lieux if l.type_lieu and str(l.type_lieu).strip().lower() == "village")
            total_csb = sum(1 for l in lieux if l.type_lieu and str(l.type_lieu).strip().lower() == "csb")
            csb_disponibles = sum(
                1
                for l in lieux
                if l.type_lieu and str(l.type_lieu).strip().lower() == "csb"
                and l.lits_disponibles is not None
                and l.lits_disponibles > 0
            )
            csb_complets = total_csb - csb_disponibles

            routes_praticables = sum(
                1 for r in routes if str(r.get("etat", "")).strip().lower() == "praticable"
            )
            routes_difficiles = sum(
                1 for r in routes if str(r.get("etat", "")).strip().lower() == "difficile"
            )
            routes_coupees = sum(1 for r in routes if str(r.get("etat", "")).strip().lower() == "coupee")

            stats = {
                "total_villages": total_villages,
                "total_csb": total_csb,
                "csb_disponibles": csb_disponibles,
                "csb_complets": csb_complets,
                "total_routes": len(routes),
                "routes_praticables": routes_praticables,
                "routes_difficiles": routes_difficiles,
                "routes_coupees": routes_coupees,
            }

            journal_admin.info("Statistiques calculées: %s", stats)
            return stats
        except Exception as e:
            journal_admin.error(f"Erreur lors du calcul des statistiques : {e}")
            raise e

    def obtenir_details_csb(self) -> list[dict]:
        lieux = self._lieu_dao.get_all()
        details = []
        for lieu in lieux:
            if lieu.type_lieu == "csb":
                details.append({
                    "id": lieu.id_lieu,
                    "nom": lieu.nom_lieu,
                    "lits_disponibles": lieu.lits_disponibles,
                    "medecin_present": lieu.medecin_present,
                    "derniere_mise_a_jour": lieu.derniere_mise_a_jour,
                    "statut": (
                        "disponible"
                        if lieu.lits_disponibles and lieu.lits_disponibles > 0
                        else "complet"
                    ),
                })
        return details

    def obtenir_reseau_routes(self) -> list[dict]:
        routes = self._route_dao.get_all()
        return [
            {
                "id_route": r["id_route"],
                "depart": r["id_lieu_depart"],
                "arrivee": r["id_lieu_arrivee"],
                "distance_km": r["distance_km"],
                "etat": r["etat"],
            }
            for r in routes
        ]
