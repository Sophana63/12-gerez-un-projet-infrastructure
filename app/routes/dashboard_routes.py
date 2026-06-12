from app.repositories.sqlite_repository import (
    get_connection
)   

def dashboardResource():

    conn = get_connection()

    cursor = conn.cursor()

    # ============================================
    # KPI SALARIÉS
    # ============================================

    cursor.execute("""
    SELECT COUNT(*)
    FROM employes
    """)

    nb_salaries = cursor.fetchone()[0]

    # ============================================
    # KPI SPORTIFS
    # ============================================

    cursor.execute("""
    SELECT COUNT(*)
    FROM eligibilite
    WHERE eligible_prime = 1
    """)

    nb_sportifs = cursor.fetchone()[0]

    # ============================================
    # SALARIES ELIGIBLE PRIME
    # ============================================

    cursor.execute("""
    SELECT COUNT(id_salarie)
    FROM eligibilite
    WHERE eligible_bien_etre = 1
    """)

    salaries_bien_etre = (
        cursor.fetchone()[0] or 0
    )

    # ============================================
    # JOURS BIEN ÊTRE
    # ============================================

    cursor.execute("""
    SELECT SUM(nb_jours_bien_etre)
    FROM eligibilite
    """)

    jours_bien_etre = (
        cursor.fetchone()[0] or 0
    )

    # ============================================
    # COUTS
    # ============================================

    cursor.execute("""
    SELECT SUM(montant_prime)
    FROM eligibilite
    """)

    couts = (
        cursor.fetchone()[0] or 0
    )

    # ============================================
    # ACTIVITES DES SALARIES
    # ============================================

    cursor.execute("""
    SELECT         
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
    LIMIT 20
    """)

    dernieres_activites = cursor.fetchall()

    # ============================================
    # ACTIVITES PAR MOIS
    # ============================================

    cursor.execute("""
    SELECT
        substr(date_debut, 1, 7) as mois,
        COUNT(*) as total
    FROM activites_sportives
    GROUP BY mois
    ORDER BY mois
    """)

    activites_par_mois = (
        cursor.fetchall()
    )

    mois_labels = [
        row["mois"]
        for row in activites_par_mois
    ]

    mois_values = [
        row["total"]
        for row in activites_par_mois
    ]

    # ============================================
    # SPORTS
    # ============================================

    cursor.execute("""
    SELECT
        type_activite,
        COUNT(*) as total
    FROM activites_sportives
    GROUP BY type_activite
    ORDER BY total DESC
    """)

    sports = cursor.fetchall()

    conn.close()

    labels = [
        row["type_activite"]
        for row in sports
    ]

    values = [
        row["total"]
        for row in sports
    ]

    return {
        "nb_salaries": nb_salaries,
        "nb_sportifs": nb_sportifs,
        "labels": labels,
        "values": values,
        "jours_bien_etre" : jours_bien_etre,
        "couts" : couts,
        "mois_labels": mois_labels,
        "mois_values": mois_values,
        "salaries_bien_etre": salaries_bien_etre,
        "dernieres_activites": [
            dict(row)
            for row in dernieres_activites
        ]
    }
    