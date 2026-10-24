import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.utils.trie import Trie, _normaliser_texte
from backend.utils.kmp import filtrer_liste, contient_motif
from database.DAO.lieuDAO import LieuDAO

journal_recherche = logging.getLogger("journal_recherche")


class ServiceRecherche:
    def __init__(self):
        self._trie = Trie()
        self._liste_villages: list[str] = []
        self._lieu_dao = LieuDAO()
        self._initialiser()

    def _initialiser(self):
        lieux = self._lieu_dao.get_all()
        for lieu in lieux:
            t = str(lieu.type_lieu or "").strip().lower()
            if t == "village":
                nom_normalise = _normaliser_texte(lieu.nom_lieu)
                self._trie.inserer(nom_normalise)
                if nom_normalise not in self._liste_villages:
                    self._liste_villages.append(nom_normalise)
        journal_recherche.info(
            "ServiceRecherche initialisé avec %s villages.", len(self._liste_villages)
        )

    def actualiser_cache(self):
        self._trie = Trie()
        self._liste_villages = []
        self._initialiser()

    def autocompletion(self, prefixe: str) -> list[str]:
        if not prefixe or not isinstance(prefixe, str):
            return []
        prefixe = prefixe.strip().lower()
        if not prefixe:
            return []
        resultats = self._trie.rechercher_prefixe(prefixe)
        journal_recherche.info(
            "Autocomplétion pour '%s': %s résultat(s).", prefixe, len(resultats)
        )
        return resultats

    def validation_exacte(self, nom: str) -> bool:
        if not nom or not isinstance(nom, str):
            return False
        nom = nom.strip().lower()
        try:
            existe = self._trie.recherche_exacte(nom)
            journal_recherche.info(
                "Validation exacte pour '%s': %s.", nom, existe
            )
            return existe
        except Exception:
            return False

    def filtrer_par_motif(self, motif: str) -> list[str]:
        if not motif or not isinstance(motif, str):
            return []
        motif = motif.strip().lower()
        if not motif:
            return []
        resultats = filtrer_liste(self._liste_villages, motif)
        journal_recherche.info(
            "Filtre KMP pour '%s': %s résultat(s).", motif, len(resultats)
        )
        return resultats

    def obtenir_tous_villages(self) -> list[str]:
        return list(self._liste_villages)
