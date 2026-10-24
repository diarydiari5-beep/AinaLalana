import logging
import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.utils.graphe import Graphe
from backend.utils.dijkstra import dijkstra, reconstruire_chemin, trouver_meilleur_csb
from backend.models.Route import Route
from database.DAO.RouteDAO import RouteDAO
from database.DAO.lieuDAO import LieuDAO

journal_routage = logging.getLogger("journal_routage")


class ServiceRoutage:
    def __init__(self):
        self._graphe = Graphe()
        self._route_dao = RouteDAO()
        self._lieu_dao = LieuDAO()
        self._ids_csb: list[str] = []
        self._routes: dict[str, Route] = {}
        self._initialiser()

    def _initialiser(self):
        self._ids_csb = []
        self._routes = {}
        self._graphe = Graphe()  
        
        lieux = self._lieu_dao.get_all()
        for lieu in lieux:
            self._graphe.ajouter_noeud(lieu.id_lieu)
            t = str(lieu.type_lieu or "").strip().lower()
            if t == "csb":
                self._ids_csb.append(lieu.id_lieu)

        rows = self._route_dao.get_all()
        for row in rows:
            route = Route(
                id_route=row["id_route"],
                id_depart=row["id_lieu_depart"],
                id_arrivee=row["id_lieu_arrivee"],
                distance=row["distance_km"],
                etat=row["etat"],
            )
            self._routes[route.id_route] = route
            self._graphe.ajouter_arc(
                route.id_lieu_depart,
                route.id_lieu_arrivee,
                route.poids,
                bidirectionnel=True,
            )

        journal_routage.info(
            "ServiceRoutage initialisé: %s nœuds, %s routes, %s CSB.",
            len(self._graphe.obtenir_tous_noeuds()),
            len(self._routes),
            len(self._ids_csb),
        )

    def ids_csb(self) -> list[str]:
        return list(self._ids_csb)

    def calculer_itineraire(self, id_depart: str, id_arrivee: str) -> dict | None:
        try:
            distances, predecesseurs = dijkstra(self._graphe, id_depart)
            chemin = reconstruire_chemin(predecesseurs, id_depart, id_arrivee)
            if not chemin:
                journal_routage.warning(
                    "Aucun chemin trouvé de %s à %s.", id_depart, id_arrivee
                )
                return None
            return {
                "chemin": chemin,
                "distance": distances.get(id_arrivee, math.inf),
                "predecesseurs": predecesseurs,
            }
        except Exception as exc:
            journal_routage.error(
                "Erreur calcul itinéraire %s -> %s: %s", id_depart, id_arrivee, exc
            )
            return None

    def recommander_meilleur_csb(
        self, id_depart: str, disponibilites: dict[str, bool]
    ) -> dict | None:
        try:
            return trouver_meilleur_csb(
                self._graphe, id_depart, self._ids_csb, disponibilites
            )
        except Exception as exc:
            journal_routage.error(
                "Erreur recommandation CSB depuis %s: %s", id_depart, exc
            )
            return None

    def appliquer_signalement(self, id_route: int, nouvel_etat: str):
        if id_route not in self._routes:
            journal_routage.warning("Route %s introuvable.", id_route)
            return
            
        route = self._routes[id_route]
        route.etat = nouvel_etat
        self._graphe.mettre_a_jour_poids(
            route.id_lieu_depart, route.id_lieu_arrivee, route.poids
        )
        self._route_dao.update_etat(id_route, nouvel_etat)
        journal_routage.info(
            "Route %s mise à jour: %s -> %s (poids=%s)",
            id_route,
            route.id_lieu_depart,
            route.id_lieu_arrivee,
            route.poids,
        )

    def obtenir_etat_route(self, id_route: int) -> str | None:
        route = self._routes.get(id_route)
        return route.etat if route else None

    def obtenir_toutes_routes(self) -> list[dict]:
        resultats = []
        for rid, route in self._routes.items():
            resultats.append({
                "id_route": rid,
                "depart": route.id_lieu_depart,
                "arrivee": route.id_lieu_arrivee,
                "distance_km": route.distance_km,
                "etat": route.etat,
                "poids": route.poids,
            })
        return resultats
