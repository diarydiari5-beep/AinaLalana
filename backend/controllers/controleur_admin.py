import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.services.service_admin import ServiceAdmin
from backend.services.service_csb import ServiceCSB
from backend.services.service_routage import ServiceRoutage

journal_ctrl = logging.getLogger("journal_controleur_admin")


class ControleurAdmin:
    def __init__(self):
        self._service_admin = ServiceAdmin()
        self._service_csb = ServiceCSB()
        self._service_routage = ServiceRoutage()

    def dashboard(self) -> dict:
        stats = self._service_admin.obtenir_statistiques()
        csb_details = self._service_admin.obtenir_details_csb()
        routes = self._service_admin.obtenir_reseau_routes()

        alertes = []
        if stats["routes_coupees"] > 0:
            alertes.append(
                f"{stats['routes_coupees']} route(s) coupée(s) détectée(s)."
            )
        if stats["csb_complets"] > 0:
            alertes.append(
                f"{stats['csb_complets']} CSB complet(s) nécessitent attention."
            )

        return {
            "succes": True,
            "dashboard": {
                "statistiques": stats,
                "csb": csb_details,
                "routes": routes,
                "alertes": alertes,
            },
        }

    def etat_reseau(self) -> dict:
        routes = self._service_admin.obtenir_reseau_routes()
        csb_liste = self._service_csb.obtenir_tous_csb()
        return {
            "succes": True,
            "reseau": {
                "routes": routes,
                "csb": csb_liste,
            },
        }

    def actualiser_cache_csb(self) -> dict:
        self._service_csb.actualiser_cache()
        return {"succes": True, "message": "Cache CSB actualisé."}
