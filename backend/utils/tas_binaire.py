"""
Structure : Tas binaire min-heap (manuel) — file de priorité pour Dijkstra

"""

import logging


journal_tas = logging.getLogger("journal_tas")


class TasBinaireMin:
    def __init__(self) -> None:
        """
        Initialise un tas vide. Stockage interne : liste Python
        """
        self._elements: list[tuple[float, str]] = []

    def inserer(self, priorite: float, identifiant: str) -> None:
        """
        Insère (priorite, identifiant) et rétablit la propriété du tas.

        
        """
        if identifiant is None or not isinstance(identifiant, str):
            raise TypeError("L'identifiant doit être une chaîne de caractères (str).")
        if not isinstance(priorite, (int, float)):
            raise TypeError("La priorité doit être un nombre (int ou float).")

        priorite_element = float(priorite)
        self._elements.append((priorite_element, identifiant))
        journal_tas.info("Insertion dans le tas: (priorite=%s, identifiant=%s)", priorite_element, identifiant)
        self._remonter(len(self._elements) - 1)

    def extraire_minimum(self) -> tuple[float, str]:
        """
        Extrait et retourne l'élément de plus faible priorité.
        Lève une exception si le tas est vide.

        """
        if self.est_vide():
            raise IndexError("Impossible d'extraire le minimum : le tas est vide.")

        element_minimum = self._elements[0]

        dernier_indice = len(self._elements) - 1
        if dernier_indice == 0:
            self._elements.pop()
            journal_tas.info("Extraction du minimum: %s", element_minimum)
            return element_minimum

        self._elements[0] = self._elements[dernier_indice]
        self._elements.pop()
        self._descendre(0)

        journal_tas.info("Extraction du minimum: %s", element_minimum)
        return element_minimum

    def est_vide(self) -> bool:
        """
        Retourne True si le tas ne contient aucun élément.
        """
        return len(self._elements) == 0

    def taille(self) -> int:
        """
        Retourne le nombre d'éléments dans le tas.

        """
        return len(self._elements)

    def _remonter(self, indice: int) -> None:
        """
        Remonte l'élément à 'indice' pour rétablir la propriété min-heap
        (appelé après insertion).

        """
        if not isinstance(indice, int):
            raise TypeError("L'indice doit être un entier (int).")
        if indice < 0 or indice >= len(self._elements):
            raise IndexError("Indice hors limites pour _remonter.")

        indice_courant = indice
        while indice_courant > 0:
            indice_parent = (indice_courant - 1) // 2

            priorite_courante, identifiant_courant = self._elements[indice_courant]
            priorite_parent, identifiant_parent = self._elements[indice_parent]

            # Si le parent est déjà plus petit ou égal la propriété du tas est respectée.
            if priorite_parent <= priorite_courante:
                break

            # Sinon on échange parent/enfant et on continue à remonter.
            self._elements[indice_courant] = (priorite_parent, identifiant_parent)
            self._elements[indice_parent] = (priorite_courante, identifiant_courant)

            indice_courant = indice_parent

    def _descendre(self, indice: int) -> None:
        """
        Descend l'élément à 'indice' pour rétablir la propriété min-heap
        appelé après extraction
        """
        if not isinstance(indice, int):
            raise TypeError("L'indice doit être un entier (int).")
        if indice < 0 or indice >= len(self._elements):
            raise IndexError("Indice hors limites pour _descendre.")

        indice_courant = indice
        taille_tas = len(self._elements)

        while True:
            indice_enfant_gauche = 2 * indice_courant + 1
            indice_enfant_droit = 2 * indice_courant + 2

            indice_plus_petit = indice_courant

            if indice_enfant_gauche < taille_tas:
                priorite_gauche, identifiant_gauche = self._elements[indice_enfant_gauche]
                priorite_plus_petit, identifiant_plus_petit = self._elements[indice_plus_petit]
                if priorite_gauche < priorite_plus_petit:
                    indice_plus_petit = indice_enfant_gauche

            if indice_enfant_droit < taille_tas:
                priorite_droit, identifiant_droit = self._elements[indice_enfant_droit]
                priorite_plus_petit, identifiant_plus_petit = self._elements[indice_plus_petit]
                if priorite_droit < priorite_plus_petit:
                    indice_plus_petit = indice_enfant_droit

            if indice_plus_petit == indice_courant:
                break

            # Échange avec l'enfant le plus petit.
            element_courant = self._elements[indice_courant]
            element_plus_petit = self._elements[indice_plus_petit]
            self._elements[indice_courant] = element_plus_petit
            self._elements[indice_plus_petit] = element_courant

            indice_courant = indice_plus_petit


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    tas = TasBinaireMin()

    # Exemple 1 : insertion simple
    tas.inserer(12.0, "csb-antsirabe")
    tas.inserer(10.0, "csb-ambalavao")
    tas.inserer(15.0, "csb-ambositra")
    journal_tas.info("Taille après insertions = %s", tas.taille())

    # Exemple 2 : extraction ordonnée (min-heap)
    premier = tas.extraire_minimum()
    deuxieme = tas.extraire_minimum()
    journal_tas.info("Deux extractions = %s puis %s", premier, deuxieme)

    # Exemple 3 : état du tas
    journal_tas.info("Tas vide ? %s (taille=%s)", tas.est_vide(), tas.taille())

