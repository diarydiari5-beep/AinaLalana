import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.services.service_recherche import ServiceRecherche
from backend.services.service_routage import ServiceRoutage
from backend.services.service_csb import ServiceCSB
from backend.services.service_signalement import ServiceSignalement
from backend.services.service_auth import ServiceAuth
from backend.models.Itineraire import Itineraire
from backend.models.EtapeItineraire import EtapeItineraire

journal_ctrl = logging.getLogger("journal_controleur_citoyen")


class ControleurCitoyen:
    def __init__(self):
        self._service_recherche = ServiceRecherche()
        self._service_routage = ServiceRoutage()
        self._service_csb = ServiceCSB()
        self._service_signalement = ServiceSignalement()
        self._service_auth = ServiceAuth()

    def rechercher_village(self, requete: str) -> dict:
        if not requete:
            return {"succes": False, "resultats": [], "message": "Requête vide."}
        resultats = self._service_recherche.autocompletion(requete)
        if not resultats:
            resultats = self._service_recherche.filtrer_par_motif(requete)
        return {
            "succes": True,
            "resultats": resultats[:10],
            "total": len(resultats),
        }

    def valider_village(self, nom: str) -> dict:
        valide = self._service_recherche.validation_exacte(nom)
        return {
            "succes": valide,
            "message": (
                "Village trouvé." if valide else "Village non reconnu."
            ),
        }

    def obtenir_csb_disponibles(self) -> dict:
        csb_liste = self._service_csb.obtenir_tous_csb()
        return {"succes": True, "csb": csb_liste, "total": len(csb_liste)}

    def calculer_itineraire(self, id_depart: str) -> dict:
        disponibilites = self._service_csb.obtenir_disponibilites()
        recommandation = self._service_routage.recommander_meilleur_csb(
            id_depart, disponibilites
        )
        if not recommandation:
            return {
                "succes": False,
                "message": "Aucun CSB accessible et disponible depuis ce village.",
            }
        return {
            "succes": True,
            "recommendation": recommandation,
        }

    def afficher_detail_trajet(self, id_depart: str, id_arrivee: str) -> dict:
        itineraire = self._service_routage.calculer_itineraire(
            id_depart, id_arrivee
        )
        if not itineraire:
            return {
                "succes": False,
                "message": "Aucun itinéraire trouvé entre ces lieux.",
            }
        etapes_detail = []
        for i, id_lieu in enumerate(itineraire["chemin"]):
            etape = EtapeItineraire(
                id_etape=i + 1, id_lieu=id_lieu, ordre=i + 1
            )
            etapes_detail.append(
                {"ordre": etape.ordre, "id_lieu": etape.id_lieu}
            )
        return {
            "succes": True,
            "itineraire": {
                "chemin": itineraire["chemin"],
                "distance_km": itineraire["distance"],
                "etapes": etapes_detail,
                "nb_etapes": len(etapes_detail),
            },
        }

    def signaler_route(
        self, id_route: int, etat: str, commentaire: str = ""
    ) -> dict:
        session = self._service_auth.obtenir_session()
        if not session:
            return {"succes": False, "message": "Vous devez être connecté."}
        ok = self._service_signalement.enregistrer_signalement_citoyen(
            session["id_utilisateur"], id_route, etat, commentaire, self._service_routage
        )
        if ok:
            msg = (
                "Demande de réouverture enregistrée. En attente de validation par un administrateur."
                if etat == "praticable"
                else "Signalement enregistré."
            )
            return {"succes": True, "message": msg}
        return {
            "succes": False,
            "message": "Erreur lors du signalement.",
        }
