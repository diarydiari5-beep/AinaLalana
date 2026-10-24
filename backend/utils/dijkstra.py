"""
Algorithme : Dijkstra poids non négatifs avec tas binaire min file de priorité

"""

import logging
import math

from backend.utils.tas_binaire import TasBinaireMin
from backend.utils.graphe import Graphe


journal_dijkstra = logging.getLogger("journal_dijkstra")


def dijkstra(graphe: Graphe, id_depart: str) -> tuple[dict[str, float], dict[str, str | None]]:
    if graphe is None:
        raise TypeError("Le graphe ne doit pas être None.")
    if id_depart is None or not isinstance(id_depart, str):
        raise TypeError("L'identifiant de départ doit être une chaîne (str).")

    liste_noeuds = graphe.obtenir_tous_noeuds()
    if id_depart not in liste_noeuds:
        raise KeyError(f"Nœud de départ introuvable dans le graphe : {id_depart!r}")

    distances: dict[str, float] = {}
    predecesseurs: dict[str, str | None] = {}

    indice = 0
    while indice < len(liste_noeuds):
        id_noeud = liste_noeuds[indice]
        distances[id_noeud] = math.inf
        predecesseurs[id_noeud] = None
        indice += 1

    distances[id_depart] = 0.0

    file_priorite = TasBinaireMin()
    file_priorite.inserer(0.0, id_depart)

    while not file_priorite.est_vide():
        distance_extraite, id_noeud_extrait = file_priorite.extraire_minimum()
        journal_dijkstra.info(
            "Extraction file de priorité: noeud=%s, distance=%s",
            id_noeud_extrait,
            distance_extraite,
        )

        # Filtrage des entrées obsolètes (absence de decrease-key).
        if distance_extraite > distances[id_noeud_extrait]:
            continue

        arcs = getattr(graphe, "_liste_adjacence", {}).get(id_noeud_extrait)
        if arcs is None:
            continue

        indice_arc = 0
        while indice_arc < len(arcs):
            arc = arcs[indice_arc]
            id_voisin = arc.destination
            poids_arc = arc.poids

            if poids_arc == math.inf:
                journal_dijkstra.info(
                    "Arc coupé ignoré: %s -> %s (poids=inf)",
                    id_noeud_extrait,
                    id_voisin,
                )
                indice_arc += 1
                continue

            # Relaxation
            nouvelle_distance = distance_extraite + float(poids_arc)
            if nouvelle_distance < distances.get(id_voisin, math.inf):
                distances[id_voisin] = nouvelle_distance
                predecesseurs[id_voisin] = id_noeud_extrait
                journal_dijkstra.info(
                    "Relaxation: %s -> %s, nouvelle_distance=%s",
                    id_noeud_extrait,
                    id_voisin,
                    nouvelle_distance,
                )
                file_priorite.inserer(nouvelle_distance, id_voisin)

            indice_arc += 1

    return distances, predecesseurs


def reconstruire_chemin(predecesseurs: dict[str, str | None], id_depart: str, id_arrivee: str) -> list[str]:
    """
    Reconstruit le chemin complet de 'id_depart' à 'id_arrivee' depuis le dict
    des prédécesseurs.

    Retourne la liste ordonnée des IDs de nœuds traversés.
    Retourne une liste vide si le chemin n'existe pas.
    """
    if predecesseurs is None:
        raise TypeError("Le dictionnaire des prédécesseurs ne doit pas être None.")
    if not isinstance(predecesseurs, dict):
        raise TypeError("Les prédécesseurs doivent être un dict {str: str | None}.")
    if id_depart is None or id_arrivee is None:
        raise TypeError("Les identifiants de départ/arrivée ne doivent pas être None.")
    if not isinstance(id_depart, str) or not isinstance(id_arrivee, str):
        raise TypeError("Les identifiants de départ/arrivée doivent être des chaînes (str).")

    if id_depart == id_arrivee:
        return [id_depart]

    # Remontée depuis l'arrivée jusqu'au départ.
    chemin_inverse: list[str] = []
    id_courant = id_arrivee

    while id_courant is not None:
        chemin_inverse.append(id_courant)
        if id_courant == id_depart:
            break
        id_courant = predecesseurs.get(id_courant)

    # Si on n'a pas atteint le départ, il n'existe pas de chemin.
    if len(chemin_inverse) == 0 or chemin_inverse[len(chemin_inverse) - 1] != id_depart:
        return []

    # Inversion manuelle pour obtenir l'ordre départ -> arrivée.
    chemin: list[str] = []
    indice = len(chemin_inverse) - 1
    while indice >= 0:
        chemin.append(chemin_inverse[indice])
        indice -= 1

    return chemin


def trouver_meilleur_csb(
    graphe: Graphe,
    id_depart: str,
    ids_csb: list[str],
    disponibilites: dict[str, bool],
) -> dict | None:
    """
    Parmi les CSB accessibles et disponibles (disponibilites[id_csb] == True)
    retourne le CSB avec la distance minimale depuis id_depart

    Retourne un dict :
      { 'id_csb': str, 'distance': float, 'chemin': list[str] }
    Retourne None si aucun CSB n'est accessible et disponible
    """
    if graphe is None:
        raise TypeError("Le graphe ne doit pas être None.")
    if id_depart is None or not isinstance(id_depart, str):
        raise TypeError("L'identifiant de départ doit être une chaîne (str).")
    if ids_csb is None or not isinstance(ids_csb, list):
        raise TypeError("ids_csb doit être une liste de chaînes (list[str]).")
    if disponibilites is None or not isinstance(disponibilites, dict):
        raise TypeError("disponibilites doit être un dictionnaire {str: bool}.")

    distances, predecesseurs = dijkstra(graphe, id_depart)

    meilleur_id_csb = None
    meilleure_distance = math.inf

    indice = 0
    while indice < len(ids_csb):
        id_csb = ids_csb[indice]
        if not isinstance(id_csb, str):
            raise TypeError("Chaque id_csb doit être une chaîne (str).")

        est_disponible = disponibilites.get(id_csb, False)
        distance_csb = distances.get(id_csb, math.inf)

        if est_disponible and distance_csb != math.inf and distance_csb < meilleure_distance:
            meilleur_id_csb = id_csb
            meilleure_distance = distance_csb

        indice += 1

    if meilleur_id_csb is None:
        journal_dijkstra.info("Aucun CSB accessible et disponible depuis %s.", id_depart)
        return None

    chemin = reconstruire_chemin(predecesseurs, id_depart, meilleur_id_csb)
    resultat = {"id_csb": meilleur_id_csb, "distance": float(meilleure_distance), "chemin": chemin}
    journal_dijkstra.info("CSB retenu: %s (distance=%s, chemin=%s)", meilleur_id_csb, meilleure_distance, chemin)
    return resultat


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # -------------------------
    # Scénario 1 : CSB le plus proche sans médecin -> CSB suivant
    # -------------------------
    graphe_1 = Graphe()
    graphe_1.ajouter_arc("ambohimanambola", "antsirabe", 5.0)
    graphe_1.ajouter_arc("antsirabe", "csb-antsirabe", 7.0)      # total 12
    graphe_1.ajouter_arc("ambohimanambola", "csb-ambalavao", 10.0)  # total 10 (mais sans médecin)
    graphe_1.ajouter_arc("ambohimanambola", "ambositra", 9.0)
    graphe_1.ajouter_arc("ambositra", "csb-ambositra", 6.0)      # total 15

    disponibilites_1 = {"csb-ambalavao": False, "csb-antsirabe": True, "csb-ambositra": True}
    resultat_1 = trouver_meilleur_csb(
        graphe_1,
        "ambohimanambola",
        ["csb-ambalavao", "csb-antsirabe", "csb-ambositra"],
        disponibilites_1,
    )
    journal_dijkstra.info("SCENARIO 1 résultat = %s", resultat_1)

    # -------------------------
    # Scénario 2 : route directe coupée -> chemin alternatif
    # -------------------------
    graphe_2 = Graphe()
    graphe_2.ajouter_arc("ambohimanambola", "csb-ambalavao", 10.0)  # direct (sera coupé)
    graphe_2.ajouter_arc("ambohimanambola", "antsirabe", 5.0)
    graphe_2.ajouter_arc("antsirabe", "village-x", 4.0)
    graphe_2.ajouter_arc("village-x", "csb-ambalavao", 5.0)        # alternatif total 14

    graphe_2.mettre_a_jour_poids("ambohimanambola", "csb-ambalavao", math.inf)
    distances_2, predecesseurs_2 = dijkstra(graphe_2, "ambohimanambola")
    chemin_2 = reconstruire_chemin(predecesseurs_2, "ambohimanambola", "csb-ambalavao")
    journal_dijkstra.info("SCENARIO 2 chemin = %s", chemin_2)
    journal_dijkstra.info("SCENARIO 2 distance totale = %s", distances_2.get("csb-ambalavao"))

    # -------------------------
    # Scénario 3 : CSB éloigné mais seul accessible et disponible
    # -------------------------
    graphe_3 = Graphe()
    graphe_3.ajouter_arc("ambohimanambola", "antsirabe", 6.0)
    graphe_3.ajouter_arc("antsirabe", "fianarantsoa", 8.0)
    graphe_3.ajouter_arc("fianarantsoa", "csb-toliara", 16.0)  # total 30

    # csb-ambalavao existe mais non connecté ici, et csb-antsirabe est indisponible
    graphe_3.ajouter_noeud("csb-antsirabe")
    graphe_3.ajouter_noeud("csb-ambalavao")

    disponibilites_3 = {"csb-ambalavao": True, "csb-antsirabe": False, "csb-toliara": True}
    resultat_3 = trouver_meilleur_csb(
        graphe_3,
        "ambohimanambola",
        ["csb-ambalavao", "csb-antsirabe", "csb-toliara"],
        disponibilites_3,
    )
    journal_dijkstra.info("SCENARIO 3 résultat = %s", resultat_3)

