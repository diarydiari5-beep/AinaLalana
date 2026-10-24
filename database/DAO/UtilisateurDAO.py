from .ConnexionBase import ConnexionBase

class UtilisateurDAO:
    @property
    def connection(self):
        return ConnexionBase.get_instance()

    def verifier_connexion(self, email, mdp):
        """Vérifie si l'utilisateur existe et retourne ses infos (dont son rôle)"""
        curseur = self.connection.cursor(dictionary=True)
        query = (
            "SELECT id_utilisateur, nom, prenom, email, role, id_csb "
            "FROM utilisateurs WHERE email = %s AND mdp = %s"
        )
        curseur.execute(query, (email, mdp))
        user = curseur.fetchone()
        curseur.close()
        return user