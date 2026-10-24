from .ConnexionBase import ConnexionBase
from backend.models.Lieu import Lieu

class LieuDAO:
    @property
    def connection(self):
        return ConnexionBase.get_instance()

    def get_all(self):
        curseur = self.connection.cursor(dictionary=True)
        query = "SELECT id_lieu, nom_lieu, type, lits_disponibles, medecin_present, derniere_mise_a_jour FROM lieux"
        curseur.execute(query)
        resultats = curseur.fetchall()
        
        lieux = []
        for row in resultats:
            lieu = Lieu(
                id_lieu=row['id_lieu'],
                nom_lieu=row['nom_lieu'],
                type_lieu=row['type'],
                lits_dispo=row['lits_disponibles'],
                medecin_present=row['medecin_present'],
                derniere_maj=row['derniere_mise_a_jour']
            )
            lieux.append(lieu)
        
        curseur.close()
        return lieux