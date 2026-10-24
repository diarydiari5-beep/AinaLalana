from .ConnexionBase import ConnexionBase

class SignalementDAO:
    @property
    def connection(self):
        return ConnexionBase.get_instance()

    def creer(self, id_user, id_route, etat, commentaire):
        """Enregistre un nouveau signalement dans la base de données[cite: 2]"""
        curseur = self.connection.cursor()
        query = """INSERT INTO signalements (id_utilisateur, id_route, etat_signale, commentaire) 
                   VALUES (%s, %s, %s, %s)"""
        curseur.execute(query, (id_user, id_route, etat, commentaire))
        self.connection.commit()
        curseur.close()

    def get_all(self):
        curseur = self.connection.cursor(dictionary=True)
        query = """SELECT s.id_signalement, s.id_utilisateur, s.id_route, s.etat_signale,
                          s.date_signalement, s.commentaire,
                          u.nom AS user_nom, u.prenom AS user_prenom
                   FROM signalements s
                   JOIN utilisateurs u ON s.id_utilisateur = u.id_utilisateur
                   ORDER BY s.date_signalement DESC"""
        curseur.execute(query)
        resultats = curseur.fetchall()
        curseur.close()
        return resultats

    def supprimer(self, id_signalement):
        curseur = self.connection.cursor()
        query = "DELETE FROM signalements WHERE id_signalement = %s"
        curseur.execute(query, (id_signalement,))
        self.connection.commit()
        curseur.close()