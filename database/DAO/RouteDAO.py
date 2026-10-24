from .ConnexionBase import ConnexionBase

class RouteDAO:
    @property
    def connection(self):
        return ConnexionBase.get_instance()

    def get_all(self):
        """Récupère toutes les routes pour construire le graphe de Dijkstra"""
        curseur = self.connection.cursor(dictionary=True)
        # On récupère les distances et l'état des routes
        query = "SELECT id_route, id_lieu_depart, id_lieu_arrivee, distance_km, etat FROM routes"
        curseur.execute(query)
        resultats = curseur.fetchall()
        curseur.close()
        return resultats

    def update_etat(self, id_route, nouvel_etat):
        """Met à jour l'état d'une route (praticable, difficile, coupee)"""
        curseur = self.connection.cursor()
        query = "UPDATE routes SET etat = %s WHERE id_route = %s"
        curseur.execute(query, (nouvel_etat, id_route))
        self.connection.commit()
        curseur.close()