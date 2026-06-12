from flask_restx import (
    Namespace,
    Resource
)

from app.repositories.sqlite_repository import (
    get_connection
)

api = Namespace(
    "employes",
    description="Gestion des employés"
)

@api.route("/")
class EmployesResource(Resource):

    def get(self):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""
        SELECT *
        FROM employes
        LIMIT 100
        """)

        rows = [
            dict(row)
            for row in cursor.fetchall()
        ]

        conn.close()

        return rows