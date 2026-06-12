from flask_restx import (
    Namespace,
    Resource
)

from app.repositories.sqlite_repository import (
    get_connection
)

# ============================================
# NAMESPACE
# ============================================

api = Namespace(
    "eligibilite",
    description="Gestion des primes sportives"
)

# ============================================
# ROUTE
# ============================================

@api.route("/")
class EligibiliteResource(Resource):

    def get(self):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""
        SELECT *
        FROM eligibilite
        LIMIT 100
        """)

        rows = [
            dict(row)
            for row in cursor.fetchall()
        ]

        conn.close()

        return rows