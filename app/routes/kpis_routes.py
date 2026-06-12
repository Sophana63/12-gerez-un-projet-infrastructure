from flask_restx import (
    Namespace,
    Resource
)

from app.repositories.sqlite_repository import (
    get_connection
)

api = Namespace(
    "kpis",
    description="Indicateurs RH"
)

@api.route("/")
class KpisResource(Resource):

    def get(self):

        conn = get_connection()

        cursor = conn.cursor()

        # ============================================
        # NOMBRE SALARIÉS
        # ============================================

        cursor.execute("""
        SELECT COUNT(*)
        FROM employes
        """)

        nb_salaries = cursor.fetchone()[0]

        # ============================================
        # SPORTIFS
        # ============================================

        cursor.execute("""
        SELECT COUNT(*)
        FROM eligibilite
        WHERE eligible_prime = 1
        """)

        nb_sportifs = cursor.fetchone()[0]

        # ============================================
        # POURCENTAGE SPORTIFS
        # ============================================

        pourcentage_sportifs = round(
            (
                nb_sportifs / nb_salaries
            ) * 100,
            2
        )

        # ============================================
        # COÛT TOTAL PRIMES
        # ============================================

        cursor.execute("""
        SELECT SUM(montant_prime)
        FROM eligibilite
        """)

        cout_total_primes = (
            cursor.fetchone()[0] or 0
        )

        # ============================================
        # TOTAL JOURS BIEN ÊTRE
        # ============================================

        cursor.execute("""
        SELECT SUM(nb_jours_bien_etre)
        FROM eligibilite
        """)

        jours_bien_etre = (
            cursor.fetchone()[0] or 0
        )

        # ============================================
        # SALARIÉS AYANT DES JOURS BIEN ÊTRE
        # ============================================

        cursor.execute("""
        SELECT COUNT(*)
        FROM eligibilite
        WHERE nb_jours_bien_etre > 0
        """)

        nb_salaries_jours_bien_etre = (
            cursor.fetchone()[0]
        )

        # ============================================
        # NOMBRE TOTAL ACTIVITÉS
        # ============================================

        cursor.execute("""
        SELECT COUNT(*)
        FROM activites_sportives
        """)

        nb_activites = cursor.fetchone()[0]

        # ============================================
        # DISTANCE TOTALE
        # ============================================

        cursor.execute("""
        SELECT SUM(distance_m)
        FROM activites_sportives
        """)

        distance_totale_m = (
            cursor.fetchone()[0] or 0
        )

        distance_totale_km = round(
            distance_totale_m / 1000,
            2
        )

        # ============================================
        # SPORT LE PLUS PRATIQUÉ
        # ============================================

        cursor.execute("""
        SELECT
            type_activite,
            COUNT(*) as total
        FROM activites_sportives
        GROUP BY type_activite
        ORDER BY total DESC
        LIMIT 1
        """)

        sport_favori = cursor.fetchone()

        # ============================================
        # COÛT GLOBAL ESTIMÉ
        # ============================================

        COUT_JOUR_BIEN_ETRE = 180

        cout_jours_bien_etre = (
            jours_bien_etre
            * COUT_JOUR_BIEN_ETRE
        )

        cout_global = round(
            cout_total_primes
            + cout_jours_bien_etre,
            2
        )

        conn.close()

        return {

            # ========================================
            # RH
            # ========================================

            "nb_salaries":
                nb_salaries,

            "nb_sportifs":
                nb_sportifs,

            "pourcentage_sportifs":
                pourcentage_sportifs,

            # ========================================
            # FINANCE
            # ========================================

            "cout_total_primes":
                round(cout_total_primes, 2),

            "cout_jours_bien_etre":
                round(cout_jours_bien_etre, 2),

            "cout_global_estime":
                cout_global,

            # ========================================
            # BIEN ÊTRE
            # ========================================

            "jours_bien_etre":
                jours_bien_etre,

            "nb_salaries_jours_bien_etre":
                nb_salaries_jours_bien_etre,

            # ========================================
            # SPORT
            # ========================================

            "nb_activites":
                nb_activites,

            "distance_totale_km":
                distance_totale_km,

            "sport_le_plus_pratique":
                sport_favori["type_activite"],

            "nb_pratiques_sport":
                sport_favori["total"]
        }