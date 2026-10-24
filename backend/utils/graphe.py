"""
Structure : Graphe pondéré (orienté / non-orienté) en listes d'adjacence.

Rôle dans AinaMobile :
- Module backend autonome destiné à la couche service (ex: dijkstra.py).
- Représente le réseau routier rural (villages / CSB) avec poids = distance × coefficient_état.
- Supporte `math.inf` pour marquer une route coupée : l'arc existe mais est inaccessible.
"""

import logging
import math


journal_graphe = logging.getLogger("journal_graphe")


class Arc:
    """
    Arc sortant d'un nœud.

    Complexité :
    - Espace : O(1) par arc
    """

    def __init__(self, destination: str, poids: float) -> None:
        self.destination = destination
        self.poids = poids


class Graphe:
    def __init__(self) -> None:
        self._liste_adjacence: dict[str, list[Arc]] = {}

    def ajouter_noeud(self, id_noeud: str) -> None:
        """
        Ajoute un nœud. Idempotent.

        Complexité :
        - Temps : O(1) amorti
        - Espace : O(1) (structure vide si nouveau nœud)
        """
        if id_noeud is None or not isinstance(id_noeud, str):
            raise TypeError("L'identifiant du nœud doit être une chaîne de caractères (str).")
        if id_noeud.strip() == "":
            raise ValueError("L'identifiant du nœud ne doit pas être vide.")

        if id_noeud not in self._liste_adjacence:
            self._liste_adjacence[id_noeud] = []
            journal_graphe.info("Ajout d'un nœud: %s", id_noeud)

    def ajouter_arc(self, source: str, destination: str, poids: float, bidirectionnel: bool = True) -> None:
        """
        Ajoute un arc (ou deux si bidirectionnel)

        Remarques :
        - Si `poids` vaut `math.inf`, l'arc est stocké mais considéré inaccessible
        """
        if source is None or destination is None:
            raise TypeError("Source et destination ne doivent pas être None.")
        if not isinstance(source, str) or not isinstance(destination, str):
            raise TypeError("Source et destination doivent être des chaînes de caractères (str).")
        if source.strip() == "" or destination.strip() == "":
            raise ValueError("Source et destination ne doivent pas être vides.")
        try:
            poids_arc = float(poids)
        except (TypeError, ValueError):
            raise TypeError("Le poids doit être un nombre (int ou float).")
        if poids_arc < 0.0 and poids_arc != math.inf:
            raise ValueError("Le poids d'un arc doit être >= 0.0 (ou math.inf pour route coupée).")

        self.ajouter_noeud(source)
        self.ajouter_noeud(destination)

        self._liste_adjacence[source].append(Arc(destination, poids_arc))
        journal_graphe.info("Ajout d'un arc: %s -> %s (poids=%s)", source, destination, poids_arc)

        if bidirectionnel:
            self._liste_adjacence[destination].append(Arc(source, poids_arc))
            journal_graphe.info("Ajout d'un arc: %s -> %s (poids=%s)", destination, source, poids_arc)

    def mettre_a_jour_poids(self, source: str, destination: str, nouveau_poids: float) -> None:
        """
        Met à jour le poids d'un arc existant (ex : route signalée coupée).

        Comportement :
        - Met à jour l'arc `source -> destination`.
        - Si l'arc inverse `destination -> source` existe aussi, il est mis à jour également
          (utile si le graphe a été construit via `bidirectionnel=True`).
        - Un arc à `math.inf` reste présent, mais est filtré dans `obtenir_voisins`.
        """
        if source is None or destination is None:
            raise TypeError("Source et destination ne doivent pas être None.")
        if not isinstance(source, str) or not isinstance(destination, str):
            raise TypeError("Source et destination doivent être des chaînes de caractères (str).")
        try:
            poids_arc = float(nouveau_poids)
        except (TypeError, ValueError):
            raise TypeError("Le nouveau poids doit être un nombre (int ou float).")
        if poids_arc < 0.0 and poids_arc != math.inf:
            raise ValueError("Le poids d'un arc doit être >= 0.0 (ou math.inf pour route coupée).")

        if source not in self._liste_adjacence:
            raise KeyError(f"Nœud source introuvable dans le graphe : {source!r}")
        if destination not in self._liste_adjacence:
            raise KeyError(f"Nœud destination introuvable dans le graphe : {destination!r}")

        mise_a_jour_source = self._mettre_a_jour_arc_unique(source, destination, poids_arc)
        mise_a_jour_inverse = self._mettre_a_jour_arc_unique(destination, source, poids_arc)

        if not mise_a_jour_source:
            raise KeyError(f"Arc introuvable : {source!r} -> {destination!r}")

        if mise_a_jour_inverse:
            journal_graphe.info(
                "Mise à jour bidirectionnelle du poids: %s <-> %s (poids=%s)",
                source,
                destination,
                poids_arc,
            )
        else:
            journal_graphe.info("Mise à jour du poids: %s -> %s (poids=%s)", source, destination, poids_arc)

    def _mettre_a_jour_arc_unique(self, source: str, destination: str, poids_arc: float) -> bool:
        """
        Met à jour un arc s'il existe.

        Complexité :
        - Temps : O(d)
        - Espace : O(1)
        """
        liste_voisins = self._liste_adjacence.get(source)
        if liste_voisins is None:
            return False

        indice = 0
        while indice < len(liste_voisins):
            arc = liste_voisins[indice]
            if arc.destination == destination:
                arc.poids = poids_arc
                return True
            indice += 1
        return False

    def obtenir_voisins(self, id_noeud: str) -> list[tuple[str, float]]:
        """
        Retourne [(voisin, poids), ...] pour un nœud donné.

        Note :
        - Les arcs dont le poids vaut `math.inf` (route coupée) sont filtrés : ils existent
          dans le graphe mais ne sont pas retournés comme voisins praticables.

        Complexité :
        - Temps : O(d), d = nombre d'arcs sortants
        - Espace : O(d) (liste de sortie)
        """
        if id_noeud is None or not isinstance(id_noeud, str):
            raise TypeError("L'identifiant du nœud doit être une chaîne de caractères (str).")
        if id_noeud not in self._liste_adjacence:
            raise KeyError(f"Nœud introuvable dans le graphe : {id_noeud!r}")

        liste_voisins: list[tuple[str, float]] = []
        arcs = self._liste_adjacence[id_noeud]
        indice = 0
        while indice < len(arcs):
            arc = arcs[indice]
            if arc.poids != math.inf:
                liste_voisins.append((arc.destination, arc.poids))
            indice += 1

        journal_graphe.info("Voisins praticables pour %s = %s", id_noeud, liste_voisins)
        return liste_voisins

    def obtenir_tous_noeuds(self) -> list[str]:
        """
        Retourne la liste de tous les nœuds.

        Complexité :
        - Temps : O(V)
        - Espace : O(V)
        """
        liste_noeuds = list(self._liste_adjacence.keys())
        journal_graphe.info("Liste de tous les nœuds (%s) récupérée.", len(liste_noeuds))
        return liste_noeuds


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    graphe = Graphe()

    # Exemple 1 : construction simple (villages / CSB)
    graphe.ajouter_arc("ambohimanambola", "antsirabe", poids=1.0)
    graphe.ajouter_arc("antsirabe", "csb-ambalavao", poids=2.0)
    voisins_antsirabe = graphe.obtenir_voisins("antsirabe")
    journal_graphe.info("Voisins de antsirabe (avant coupure) = %s", voisins_antsirabe)

    # Exemple 2 : route signalée coupée (math.inf) et filtrage dans obtenir_voisins
    graphe.mettre_a_jour_poids("ambohimanambola", "antsirabe", math.inf)
    voisins_antsirabe_apres = graphe.obtenir_voisins("antsirabe")
    journal_graphe.info("Voisins de antsirabe (après coupure) = %s", voisins_antsirabe_apres)

    # Exemple 3 : récupération des nœuds
    tous_les_noeuds = graphe.obtenir_tous_noeuds()
    journal_graphe.info("Tous les nœuds = %s", tous_les_noeuds)

