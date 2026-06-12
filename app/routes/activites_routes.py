from flask_restx import (
    Namespace,
    Resource
)

from app.repositories.sqlite_repository import (
    get_connection
)

api = Namespace(
    "activites",
    description="Activités sportives"
)

@api.route("/")
class ActivitesResource(Resource):

    def get(self):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""
        SELECT 
            a.id,
            a.id_salarie,
            e.nom,
            e.prenom,
            a.date_debut,
            a.type_activite,
            a.distance_m,
            a.date_fin,
            a.commentaire
        FROM activites_sportives a
        LEFT JOIN employes e
        ON a.id_salarie = e.id_salarie
        ORDER BY date_debut DESC
        LIMIT 100
        """)

        rows = [
            dict(row)
            for row in cursor.fetchall()
        ]

        conn.close()

        return rows