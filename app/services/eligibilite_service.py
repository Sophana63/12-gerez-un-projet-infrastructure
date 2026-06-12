from datetime import datetime
import os

from app.config import (
    ADRESSE_ENTREPRISE,
    DISTANCE_MAX_MARCHE_KM,
    DISTANCE_MAX_VELO_KM,
    PRIME_TAUX,
    BIEN_ETRE_SEUIL_ACTIVITES,
    BIEN_ETRE_JOURS,
)

from app.repositories.sqlite_repository import (
    get_connection
)

from app.services.google_maps_service import (
    calculer_distance_google_maps
)

MODES_SPORTIFS = {
    "vélo",
    "velo",
    "trottinette",
    "course",
    "running",
    "marche",
    "marche/running"
}

PRIME_TAUX = float(os.getenv("PRIME_TAUX", 0.05))


def creer_tables():

    conn = get_connection()

    cursor = conn.cursor()

    # ============================================
    # ALERTES QUALITE
    # ============================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alertes_qualite (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_salarie INTEGER,
        type_alerte TEXT,
        description TEXT,
        valeur_observee TEXT,
        valeur_attendue TEXT,
        severite TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ============================================
    # ELIGIBILITE
    # ============================================

    cursor.execute("""
    DROP TABLE IF EXISTS eligibilite
    """)

    cursor.execute("""
    CREATE TABLE eligibilite (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_salarie INTEGER UNIQUE,
        eligible_prime INTEGER,
        montant_prime REAL,
        eligible_bien_etre INTEGER,
        nb_activites_annee INTEGER,
        nb_jours_bien_etre INTEGER,
        distance_domicile_km REAL,
        annee_calcul INTEGER
    )
    """)

    conn.commit()

    conn.close()


def valider_declaration_deplacement(
    salarie,
    distance_km
):

    conn = get_connection()

    cursor = conn.cursor()

    mode = (
        salarie["moyen_de_deplacement"] or ""
    ).lower()

    # ============================================
    # MODE NON SPORTIF
    # ============================================

    if mode not in MODES_SPORTIFS:

        conn.close()

        return False

    # ============================================
    # DISTANCE NON CALCULABLE
    # ============================================

    if distance_km is None:

        conn.close()

        return False

    # ============================================
    # LIMITES
    # ============================================

    if mode in {
        "course",
        "running",
        "marche",
        "marche/running"
    }:

        limite = DISTANCE_MAX_MARCHE_KM

    else:

        limite = DISTANCE_MAX_VELO_KM

    # ============================================
    # DISTANCE INCOHERENTE
    # ============================================

    if distance_km > limite:

        cursor.execute("""
        INSERT INTO alertes_qualite (
            id_salarie,
            type_alerte,
            description,
            valeur_observee,
            valeur_attendue,
            severite
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            salarie["id_salarie"],
            "distance_incoherente",
            (
                f"{salarie['prenom']} "
                f"{salarie['nom']} "
                f"habite à {distance_km} km"
            ),
            f"{distance_km} km",
            f"<= {limite} km",
            "warning"
        ))

        conn.commit()

        conn.close()

        return False

    conn.close()

    return True


def calculer_eligibilite_salarie(
    salarie
):

    conn = get_connection()

    cursor = conn.cursor()

    mode = (
        salarie["moyen_de_deplacement"] or ""
    ).lower()

    # ============================================
    # CALCUL DISTANCE POUR TOUS
    # ============================================

    distance_km = (
        calculer_distance_google_maps(
            salarie["adresse_du_domicile"],
            ADRESSE_ENTREPRISE,
            mode
        )
    )

    # ============================================
    # VALIDATION DECLARATION
    # ============================================

    declaration_valide = (
        valider_declaration_deplacement(
            salarie,
            distance_km
        )
    )

    # ============================================
    # PRIME
    # ============================================

    eligible_prime = (
        mode in MODES_SPORTIFS
        and declaration_valide
    )

    montant_prime = 0

    if eligible_prime:

        montant_prime = round(
            salarie["salaire_brut"]
            * PRIME_TAUX,
            2
        )

    # ============================================
    # ACTIVITES SPORTIVES
    # ============================================

    current_year = datetime.now().year

    cursor.execute("""
    SELECT COUNT(*)
    FROM activites_sportives
    WHERE id_salarie = ?
    AND strftime('%Y', date_debut) = ?
    """, (
        salarie["id_salarie"],
        str(current_year)
    ))

    nb_activites = cursor.fetchone()[0]

    # ============================================
    # BIEN ETRE
    # ============================================

    eligible_bien_etre = (
        nb_activites
        >= BIEN_ETRE_SEUIL_ACTIVITES
    )

    jours_accordes = (
        BIEN_ETRE_JOURS
        if eligible_bien_etre
        else 0
    )

    # ============================================
    # INSERT ELIGIBILITE
    # ============================================

    cursor.execute("""
    INSERT OR REPLACE INTO eligibilite (
        id_salarie,
        eligible_prime,
        montant_prime,
        eligible_bien_etre,
        nb_activites_annee,
        nb_jours_bien_etre,
        distance_domicile_km,
        annee_calcul
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        salarie["id_salarie"],
        int(eligible_prime),
        montant_prime,
        int(eligible_bien_etre),
        nb_activites,
        jours_accordes,
        distance_km,
        current_year
    ))

    conn.commit()

    conn.close()