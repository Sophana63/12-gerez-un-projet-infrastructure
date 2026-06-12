import sqlite3

from app.services.google_maps_service import (
    calculer_distance_google_maps
)

# =========================================================
# CONFIGURATION
# =========================================================

DB_PATH = "./data/avantages_sportifs.db"

# Adresse entreprise (PDF)
COMPANY_ADDRESS = "1362 Av. des Platanes, 34970 Lattes"

# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()

# =========================================================
# GLOBAL COUNTERS
# =========================================================

errors = []
warnings = []

# =========================================================
# 1. CHECK NULL EMPLOYEE IDS
# =========================================================

cursor.execute("""
SELECT COUNT(*)
FROM activites_sportives
WHERE id_salarie IS NULL
""")

count = cursor.fetchone()[0]

if count > 0:
    errors.append(
        f"[ERREUR] {count} activités sans id_salarie"
    )

# =========================================================
# 2. CHECK UNKNOWN EMPLOYEES
# =========================================================

cursor.execute("""
SELECT COUNT(*)
FROM activites_sportives a
LEFT JOIN employes e
ON a.id_salarie = e.id_salarie
WHERE e.id_salarie IS NULL
""")

count = cursor.fetchone()[0]

if count > 0:
    errors.append(
        f"[ERREUR] {count} activités liées à des salariés inconnus"
    )

# =========================================================
# 3. CHECK NEGATIVE DISTANCES
# =========================================================

cursor.execute("""
SELECT COUNT(*)
FROM activites_sportives
WHERE distance_m < 0
""")

count = cursor.fetchone()[0]

if count > 0:
    errors.append(
        f"[ERREUR] {count} distances négatives"
    )

# =========================================================
# 4. CHECK NEGATIVE DURATIONS
# =========================================================

cursor.execute("""
SELECT COUNT(*)
FROM activites_sportives
WHERE temps_ecoule_s < 0
""")

count = cursor.fetchone()[0]

if count > 0:
    errors.append(
        f"[ERREUR] {count} durées négatives"
    )

# =========================================================
# 5. CHECK END DATE BEFORE START DATE
# =========================================================

cursor.execute("""
SELECT COUNT(*)
FROM activites_sportives
WHERE date_fin < date_debut
""")

count = cursor.fetchone()[0]

if count > 0:
    errors.append(
        f"[ERREUR] {count} activités avec date_fin < date_debut"
    )

# =========================================================
# 6. CHECK FUTURE DATES
# =========================================================

cursor.execute("""
SELECT COUNT(*)
FROM activites_sportives
WHERE date_debut > datetime('now')
""")

count = cursor.fetchone()[0]

if count > 0:
    warnings.append(
        f"[WARNING] {count} activités dans le futur"
    )

# =========================================================
# 7. CHECK REALISTIC SPEEDS
# =========================================================

cursor.execute("""
SELECT
    id,
    type_activite,
    distance_m,
    temps_ecoule_s
FROM activites_sportives
WHERE distance_m IS NOT NULL
AND temps_ecoule_s > 0
""")

activities = cursor.fetchall()

for activity in activities:

    activity_id = activity[0]
    sport = activity[1]
    distance = activity[2]
    duration = activity[3]

    speed_kmh = (
        (distance / 1000)
        /
        (duration / 3600)
    )

    # Contrôles réalistes
    if sport == "Course à pied" and speed_kmh > 25:
        warnings.append(
            f"[WARNING] activité {activity_id} : vitesse course suspecte ({speed_kmh:.1f} km/h)"
        )

    elif sport == "Vélo" and speed_kmh > 60:
        warnings.append(
            f"[WARNING] activité {activity_id} : vitesse vélo suspecte ({speed_kmh:.1f} km/h)"
        )

    elif sport == "Marche" and speed_kmh > 10:
        warnings.append(
            f"[WARNING] activité {activity_id} : vitesse marche suspecte ({speed_kmh:.1f} km/h)"
        )

# =========================================================
# 8. CHECK DUPLICATES
# =========================================================

cursor.execute("""
SELECT
    id_salarie,
    date_debut,
    type_activite,
    COUNT(*)
FROM activites_sportives
GROUP BY
    id_salarie,
    date_debut,
    type_activite
HAVING COUNT(*) > 1
""")

duplicates = cursor.fetchall()

if len(duplicates) > 0:

    warnings.append(
        f"[WARNING] {len(duplicates)} doublons potentiels"
    )

# =========================================================
# 9. CHECK ELIGIBILITY RULES (PDF)
# =========================================================
#
# PDF:
# - Marche / Running <= 15 km
# - Vélo / Trottinette <= 25 km
#
# Ici :
# on vérifie simplement les déclarations RH
#
# =========================================================

cursor.execute("""
SELECT
    id_salarie,
    moyen_de_deplacement,
    adresse_du_domicile           
FROM employes
""")

employees = cursor.fetchall()

for employee in employees:

    employee_id = employee[0]

    transport = employee[1]

    home_address = employee[2]

    if not transport or not home_address:
        continue

    transport = (
        transport
        .lower()
        .strip()
    )

    # ============================================
    # VALIDATION TRANSPORT
    # ============================================

    valid_transports = [
        "velo",
        "vélo",
        "trottinette",
        "marche",
        "running",
        "voiture",
        "transport",
        "véhicule thermique"
    ]

    is_valid = any(
        t in transport
        for t in valid_transports
    )

    if not is_valid:

        warnings.append(
            f"[WARNING] salarié {employee_id} : moyen de déplacement inconnu ({transport})"
        )

        continue

    # ============================================
    # DISTANCE GOOGLE MAPS
    # ============================================

    try:

        distance_km = calculer_distance_google_maps(
            adresse_origine=home_address,
            adresse_destination="1362 Av. des Platanes, 34970 Lattes",
            mode=transport
        )

    except Exception as e:

        warnings.append(
            f"[ERROR] salarié {employee_id} : erreur Google Maps ({str(e)})"
        )

        continue

    # ============================================
    # RÈGLES MÉTIER PDF
    # ============================================

    # Marche / Running
    if (
        "marche" in transport
        or "running" in transport
    ):

        if distance_km > 15:

            warnings.append(
                f"[ALERTE] salarié {employee_id} : "
                f"{distance_km:.1f} km déclarés en marche/running"
            )

    # Vélo / Trottinette
    elif (
        "velo" in transport
        or "vélo" in transport
        or "trottinette" in transport
    ):

        if distance_km > 25:

            warnings.append(
                f"[ALERTE] salarié {employee_id} : "
                f"{distance_km:.1f} km déclarés en vélo/trottinette"
            )

# =========================================================
# REPORT
# =========================================================

print("\n===================================")
print("DATA QUALITY REPORT")
print("===================================\n")

print(f"Nombre d'erreurs : {len(errors)}")
print(f"Nombre de warnings : {len(warnings)}")

print("\n----------- ERREURS -----------\n")

if len(errors) == 0:
    print("Aucune erreur détectée")

else:
    for error in errors:
        print(error)

print("\n----------- WARNINGS -----------\n")

if len(warnings) == 0:
    print("Aucun warning détecté")

else:
    for warning in warnings:
        print(warning)

# =========================================================
# OPTIONAL EXPORT TABLE
# =========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS data_quality_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT,
    message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Insert errors
for error in errors:

    cursor.execute("""
    INSERT INTO data_quality_logs (
        level,
        message
    )
    VALUES (?, ?)
    """, (
        "ERROR",
        error
    ))

# Insert warnings
for warning in warnings:

    cursor.execute("""
    INSERT INTO data_quality_logs (
        level,
        message
    )
    VALUES (?, ?)
    """, (
        "WARNING",
        warning
    ))

conn.commit()

# =========================================================
# CLOSE
# =========================================================

conn.close()

print("\nData quality terminée")