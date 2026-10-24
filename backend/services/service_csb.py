import logging
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from database.DAO.lieuDAO import LieuDAO

journal_csb = logging.getLogger("journal_csb")


class ServiceCSB:
    def __init__(self):
        self._lieu_dao = LieuDAO()
        self._cache_csb: dict[str, dict] = {}
        self._initialiser()

    def _initialiser(self):
        lieux = self._lieu_dao.get_all()
        for lieu in lieux:
            t = str(lieu.type_lieu or "").strip().lower()
            if t == "csb":
                self._cache_csb[lieu.id_lieu] = {
                    "id": lieu.id_lieu,
                    "nom": lieu.nom_lieu,
                    "lits_disponibles": lieu.lits_disponibles,
                    "medecin_present": lieu.medecin_present,
                    "derniere_mise_a_jour": lieu.derniere_mise_a_jour,
                    "disponible": bool(lieu.medecin_present),
                }
        journal_csb.info(
            "ServiceCSB initialisé: %s CSB en cache.", len(self._cache_csb)
        )

    def obtenir_tous_csb(self) -> list[dict]:
        return list(self._cache_csb.values())

    def obtenir_csb_disponibles(self) -> list[dict]:
        return [
            csb for csb in self._cache_csb.values() if csb.get("disponible")
        ]

    def obtenir_disponibilites(self) -> dict[str, bool]:
        return {
            csb_id: csb["disponible"]
            for csb_id, csb in self._cache_csb.items()
        }

    def mettre_a_jour_csb(
        self,
        id_csb: str,
        lits_disponibles: int = None,
        medecin_present: bool = None,
    ) -> bool:
        if id_csb not in self._cache_csb:
            journal_csb.warning("CSB %s introuvable dans le cache.", id_csb)
            return False

        champs = {}
        if lits_disponibles is not None:
            champs["lits_disponibles"] = lits_disponibles
        if medecin_present is not None:
            champs["medecin_present"] = medecin_present

        if not champs:
            return False

        sql_parts = []
        sql_params = []
        for champ, valeur in champs.items():
            champ_sql = {"lits_disponibles": "lits_disponibles", "medecin_present": "medecin_present"}[champ]
            sql_parts.append(f"{champ_sql} = %s")
            sql_params.append(valeur)

        sql_params.append(id_csb)
        curseur = self._lieu_dao.connection.cursor()
        query = f"UPDATE lieux SET {', '.join(sql_parts)}, derniere_mise_a_jour = NOW() WHERE id_lieu = %s"
        curseur.execute(query, tuple(sql_params))
        self._lieu_dao.connection.commit()
        curseur.close()

        cache = self._cache_csb[id_csb]
        if lits_disponibles is not None:
            cache["lits_disponibles"] = lits_disponibles
        if medecin_present is not None:
            cache["medecin_present"] = medecin_present
            cache["disponible"] = bool(medecin_present)
        cache["derniere_mise_a_jour"] = datetime.now()

        journal_csb.info(
            "CSB %s mis à jour: %s (disponible=%s)",
            id_csb,
            champs,
            cache["disponible"],
        )
        return True

    def obtenir_csb_par_id(self, id_csb: str) -> dict | None:
        return self._cache_csb.get(id_csb)

    def actualiser_cache(self):
        self._cache_csb.clear()
        self._initialiser()
