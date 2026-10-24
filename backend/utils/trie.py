"""
Structure : Tri pour autocomplétion

"""

import logging


journal_trie = logging.getLogger("journal_trie")


ALPHABET_AUTORISE = " -abcdefghijklmnopqrstuvwxyz"


def _normaliser_texte(texte: str) -> str:
    """
    Normalise un nom en :
    - minuscule
    - accents simplifiés vers ASCII ( é -> e)
    - espaces multiples réduits
    - caractères autorisés : lettres a-z, espace, tiret
    """
    if texte is None:
        raise TypeError("Le texte à normaliser ne doit pas être None.")
    if not isinstance(texte, str):
        raise TypeError("Le texte à normaliser doit être une chaîne de caractères (str).")

    texte_minuscule = texte.strip().lower()
    if texte_minuscule == "":
        raise ValueError("Le texte à normaliser ne doit pas être vide.")

    correspondances = {
        "à": "a", "á": "a", "â": "a", "ä": "a", "ã": "a", "å": "a",
        "ç": "c",
        "è": "e", "é": "e", "ê": "e", "ë": "e",
        "ì": "i", "í": "i", "î": "i", "ï": "i",
        "ñ": "n",
        "ò": "o", "ó": "o", "ô": "o", "ö": "o", "õ": "o",
        "ù": "u", "ú": "u", "û": "u", "ü": "u",
        "ý": "y", "ÿ": "y",
        "œ": "oe",
        "æ": "ae",
        "’": "'",  # apostrophe typographique -> apostrophe simple (ensuite rejetée)
    }

    liste_caracteres_normalises: list[str] = []
    indice = 0
    while indice < len(texte_minuscule):
        caractere = texte_minuscule[indice]
        remplacement = correspondances.get(caractere)
        if remplacement is not None:
            liste_caracteres_normalises.append(remplacement)
        else:
            liste_caracteres_normalises.append(caractere)
        indice += 1

    texte_normalise = "".join(liste_caracteres_normalises)

    # Uniformisation des séparateurs, puis réduction des répétitions.
    liste_sortie: list[str] = []
    caractere_precedent = ""
    indice = 0
    while indice < len(texte_normalise):
        caractere = texte_normalise[indice]

        if caractere == "_":
            caractere = " "

        if caractere == "\t" or caractere == "\n" or caractere == "\r":
            caractere = " "

        if caractere == "'" or caractere == "." or caractere == "," or caractere == "/":
            raise ValueError(
                "Caractère non supporté dans un nom (apostrophe/ponctuation). "
                "Utiliser uniquement lettres, espaces et tirets."
            )

        if caractere == " ":
            if caractere_precedent == " ":
                indice += 1
                continue
            caractere_precedent = " "
            liste_sortie.append(" ")
            indice += 1
            continue

        if caractere == "-":
            if caractere_precedent == "-":
                indice += 1
                continue
            caractere_precedent = "-"
            liste_sortie.append("-")
            indice += 1
            continue

        # Lettres a-z uniquement
        if "a" <= caractere <= "z":
            caractere_precedent = caractere
            liste_sortie.append(caractere)
            indice += 1
            continue

        raise ValueError(
            f"Caractère non supporté dans un nom : {caractere!r}. "
            "Utiliser uniquement lettres a-z, espaces et tirets (accents autorisés)."
        )

    texte_sortie = "".join(liste_sortie).strip()
    if texte_sortie == "":
        raise ValueError("Le texte normalisé ne doit pas être vide.")
    return texte_sortie


class NoeudTrie:
    """
    Nœud du Trie.

    Attributs :
    - enfants : dictionnaire {caractere -> NoeudTrie}
    - fin_de_mot : bool indiquant si un mot se termine à ce nœud
    """

    def __init__(self) -> None:
        self.enfants: dict[str, "NoeudTrie"] = {}
        self.fin_de_mot: bool = False


class Trie:
    """
    Trie pour autocomplétion de noms normalisés

    Note :
    - Le parcours alphabétique est garanti sans tri dynamique en itérant un alphabet
      constant (`ALPHABET_AUTORISE`), ce qui convient aux contraintes de RAM/CPU
    """

    def __init__(self) -> None:
        self.racine = NoeudTrie()

    def inserer(self, mot: str) -> None:
        """
        Insère un mot dans le Trie.

        """
        mot_normalise = _normaliser_texte(mot)
        journal_trie.info("Insertion d'un mot dans le Trie: %s", mot_normalise)

        noeud_courant = self.racine
        indice = 0
        while indice < len(mot_normalise):
            caractere = mot_normalise[indice]
            noeud_enfant = noeud_courant.enfants.get(caractere)
            if noeud_enfant is None:
                noeud_enfant = NoeudTrie()
                noeud_courant.enfants[caractere] = noeud_enfant
            noeud_courant = noeud_enfant
            indice += 1

        noeud_courant.fin_de_mot = True

    def recherche_exacte(self, mot: str) -> bool:
        """
        Vérifie si 'mot' existe exactement dans le Trie.

        """
        mot_normalise = _normaliser_texte(mot)
        journal_trie.info("Recherche exacte dans le Trie: %s", mot_normalise)

        noeud_courant = self.racine
        indice = 0
        while indice < len(mot_normalise):
            caractere = mot_normalise[indice]
            noeud_enfant = noeud_courant.enfants.get(caractere)
            if noeud_enfant is None:
                return False
            noeud_courant = noeud_enfant
            indice += 1
        return noeud_courant.fin_de_mot

    def rechercher_prefixe(self, prefixe: str) -> list[str]:
        """
        Retourne tous les mots commençant par 'prefixe'

        La liste est retournée en ordre alphabétique (basé sur l'alphabet autorisé)
        """
        prefixe_normalise = _normaliser_texte(prefixe)
        journal_trie.info("Recherche par préfixe dans le Trie: %s", prefixe_normalise)

        noeud_courant = self.racine
        indice = 0
        while indice < len(prefixe_normalise):
            caractere = prefixe_normalise[indice]
            noeud_enfant = noeud_courant.enfants.get(caractere)
            if noeud_enfant is None:
                return []
            noeud_courant = noeud_enfant
            indice += 1

        # Parcours en profondeur non récursif pour éviter la récursion sur mobile.
        resultats: list[str] = []
        pile_noeuds: list[tuple[NoeudTrie, str]] = [(noeud_courant, prefixe_normalise)]

        while len(pile_noeuds) > 0:
            noeud_actuel, mot_construit = pile_noeuds.pop()
            if noeud_actuel.fin_de_mot:
                resultats.append(mot_construit)

            # Empilement inverse pour obtenir une sortie alphabétique au dépilement.
            indice_alphabet = len(ALPHABET_AUTORISE) - 1
            while indice_alphabet >= 0:
                caractere = ALPHABET_AUTORISE[indice_alphabet]
                noeud_enfant = noeud_actuel.enfants.get(caractere)
                if noeud_enfant is not None:
                    pile_noeuds.append((noeud_enfant, mot_construit + caractere))
                indice_alphabet -= 1

        return resultats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    trie = Trie()

    # Exemple 1 : insertion + autocomplétion (villages)
    trie.inserer("Ambohimanambola")
    trie.inserer("Ambalavao")
    trie.inserer("Ambositra")
    suggestions_amb = trie.rechercher_prefixe("amb")
    journal_trie.info("Suggestions pour 'amb' = %s", suggestions_amb)

    # Exemple 2 : support des noms composés / CSB (espaces, tirets)
    trie.inserer("CSB-Ambalavao")
    trie.inserer("CSB Ambalavao")  # normalisé avec espace
    suggestions_csb = trie.rechercher_prefixe("csb")
    journal_trie.info("Suggestions pour 'csb' = %s", suggestions_csb)

    # Exemple 3 : recherche exacte
    existe_antsirabe = trie.recherche_exacte("Antsirabe")
    trie.inserer("Antsirabe")
    existe_antsirabe_apres = trie.recherche_exacte("antsirabe")
    journal_trie.info("Antsirabe avant insertion=%s, après insertion=%s", existe_antsirabe, existe_antsirabe_apres)

