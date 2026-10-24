"""
Algorithme : Knuth-Morris-Pratt (KMP) — recherche de sous-chaîne 

Rôle dans AinaMobile :
- Module backend autonome utilisé par la couche service (`service_recherche.py`).
- Permet de filtrer des noms de villages/CSB (déjà normalisés en minuscule) en
  évitant la recherche naïve sur des appareils à ressources limitées.

"""

import logging


journal_kmp = logging.getLogger("journal_kmp")


def _rechercher_sous_chaine_avec_table(texte: str, motif: str, table_echec: list[int]) -> list[int]:
    """
    Variante interne de KMP utilisant une table des échecs déjà construite.

    Objectif :
    - Éviter de reconstruire la table pour des recherches répétées (filtrage de liste),
      ce qui réduit CPU/RAM en environnement contraint.
    """
    longueur_texte = len(texte)
    longueur_motif = len(motif)

    occurrences: list[int] = []
    indice_texte = 0
    indice_motif = 0

    while indice_texte < longueur_texte:
        if texte[indice_texte] == motif[indice_motif]:
            indice_texte += 1
            indice_motif += 1

            if indice_motif == longueur_motif:
                position_occurrence = indice_texte - longueur_motif
                occurrences.append(position_occurrence)
                indice_motif = table_echec[indice_motif - 1]
            continue

        if indice_motif != 0:
            indice_motif = table_echec[indice_motif - 1]
            continue

        indice_texte += 1

    return occurrences


def construire_table_echec(motif: str) -> list[int]:
    """
    Construit la table des échecs (failure function) pour le motif donné

    La table des échecs indique, pour chaque position du motif, la longueur du
    plus long préfixe propre qui est aussi un suffixe du motif jusqu'à cette position
    """
    if motif is None:
        raise TypeError("Le motif ne doit pas être None.")
    if not isinstance(motif, str):
        raise TypeError("Le motif doit être une chaîne de caractères (str).")

    longueur_motif = len(motif)
    if longueur_motif == 0:
        # Motif vide : table vide (l'appelant gère l'usage)
        journal_kmp.warning("Construction table d'échec: motif vide -> table vide.")
        return []

    # Table d'échec à construire : table_echec[position] = longueur du meilleur bord
    table_echec: list[int] = [0] * longueur_motif

    # longueur_bord = longueur du plus long préfixe/suffixe trouvé jusqu'ici
    longueur_bord = 0

    # On commence à la seconde position : le premier caractère a toujours 0
    position_motif = 1

    journal_kmp.info("Construction table d'échec pour motif (taille=%s).", longueur_motif)

    while position_motif < longueur_motif:
        # Si les caractères correspondent on peut étendre le bord courant.
        if motif[position_motif] == motif[longueur_bord]:
            longueur_bord += 1
            table_echec[position_motif] = longueur_bord
            position_motif += 1
            continue

        # Sinon, on réduit le bord courant en utilisant la table déjà construite
        if longueur_bord != 0:
            # On ne recule pas position_motif : on tente un bord plus court
            longueur_bord = table_echec[longueur_bord - 1]
            continue

        # Aucun bord possible la valeur reste 0 on avance dans le motif
        table_echec[position_motif] = 0
        position_motif += 1

    return table_echec


def rechercher_sous_chaine(texte: str, motif: str) -> list[int]:
    """
    Retourne la liste de toutes les positions (indices) où 'motif' apparaît dans 'texte'.
    Retourne une liste vide si aucune occurrence.

    """
    if texte is None or motif is None:
        raise TypeError("Le texte et le motif ne doivent pas être None.")
    if not isinstance(texte, str) or not isinstance(motif, str):
        raise TypeError("Le texte et le motif doivent être des chaînes de caractères (str).")

    longueur_texte = len(texte)
    longueur_motif = len(motif)

    # Motif vide : par convention demandée -> liste vide + avertissement.
    if longueur_motif == 0:
        journal_kmp.warning("Recherche KMP: motif vide -> aucune occurrence retournée.")
        return []

    # Si le motif est plus long que le texte, aucune occurrence possible.
    if longueur_motif > longueur_texte:
        journal_kmp.info("Recherche KMP terminée: 0 occurrence (motif plus long que texte).")
        return []

    table_echec = construire_table_echec(motif)

    occurrences = _rechercher_sous_chaine_avec_table(texte, motif, table_echec)

    journal_kmp.info("Recherche KMP terminée: %s occurrence(s) trouvée(s).", len(occurrences))
    return occurrences


def contient_motif(texte: str, motif: str) -> bool:
    """
    Retourne True si 'motif' est contenu dans 'texte', False sinon.
    Wrapper au-dessus de rechercher_sous_chaine pour un usage booléen simple.
    """
    occurrences = rechercher_sous_chaine(texte, motif)
    return len(occurrences) > 0


def filtrer_liste(noms: list[str], motif: str) -> list[str]:
    """
    Retourne tous les noms de 'noms' qui contiennent 'motif'.
    Utilisé pour filtrer la liste des villages depuis le Trie.
    """
    if noms is None:
        raise TypeError("La liste de noms ne doit pas être None.")
    if not isinstance(noms, list):
        raise TypeError("La liste de noms doit être de type list[str].")
    if motif is None:
        raise TypeError("Le motif ne doit pas être None.")
    if not isinstance(motif, str):
        raise TypeError("Le motif doit être une chaîne de caractères (str).")

    if len(motif) == 0:
        journal_kmp.warning("Filtrage: motif vide -> résultat vide.")
        return []

    table_echec = construire_table_echec(motif)

    resultat: list[str] = []
    indice = 0
    while indice < len(noms):
        nom = noms[indice]
        if not isinstance(nom, str):
            raise TypeError("Chaque élément de 'noms' doit être une chaîne de caractères (str).")

        if len(nom) >= len(motif):
            occurrences = _rechercher_sous_chaine_avec_table(nom, motif, table_echec)
        else:
            occurrences = []

        if len(occurrences) > 0:
            resultat.append(nom)
        indice += 1

    journal_kmp.info("Filtrage terminé: %s nom(s) conservé(s) sur %s.", len(resultat), len(noms))
    return resultat


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Liste d'exemples (noms déjà normalisés en minuscule par convention)
    # Le projet injectera la vraie liste via la couche service.
    liste_villages_cdc = [
        "ambohidratrimo",
        "ambohimanambola",
        "antananarivo",
        "antsirabe",
        "antsiranana",
        "ambalavao",
        "ambositra",
        "fianarantsoa",
        "mahajanga",
        "toliara",
        "toamasina",
        "morondava",
        "manakara",
        "farafangana",
        "sambava",
    ]

    # Exemple 1 : motif exact présent dans la liste
    motif_1 = "ambohidratrimo"
    resultat_1 = filtrer_liste(liste_villages_cdc, motif_1)
    journal_kmp.info("Exemple 1 - motif=%s -> %s", motif_1, resultat_1)

    # Exemple 2 : motif partiel "antsira" -> Antsirabe + Antsiranana
    motif_2 = "antsira"
    resultat_2 = filtrer_liste(liste_villages_cdc, motif_2)
    journal_kmp.info("Exemple 2 - motif=%s -> %s", motif_2, resultat_2)

    # Exemple 3 : motif introuvable -> liste vide
    motif_3 = "tsiroaroa"
    resultat_3 = filtrer_liste(liste_villages_cdc, motif_3)
    journal_kmp.info("Exemple 3 - motif=%s -> %s", motif_3, resultat_3)

