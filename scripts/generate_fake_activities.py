import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

# =========================================================
# CONFIGURATION
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

DB_PATH = ROOT_DIR / "data" / "avantages_sportifs.db"

NB_MIN_ACTIVITIES = 10
NB_MAX_ACTIVITIES = 80

TODAY = datetime.now()

# =========================================================
# SPORTS CONFIGURATION
# =========================================================

SPORTS = {
    "Course à pied": {
        "distance_min": 3000,
        "distance_max": 20000,
        "speed_kmh": (8, 14),
        "comments": [
            "Belle séance 🔥",
            "Reprise du sport :)",
            "Sortie avant le travail",
            "Très bonnes sensations",
            "Préparation semi-marathon",
            "Footing du dimanche"
        ]
    },

    "Vélo": {
        "distance_min": 5000,
        "distance_max": 80000,
        "speed_kmh": (18, 32),
        "comments": [
            "Sortie vélo au top 🚴",
            "Vent compliqué aujourd'hui",
            "Belle sortie longue",
            "Trajet domicile travail",
            "Sortie récupération"
        ]
    },

    "Randonnée": {
        "distance_min": 4000,
        "distance_max": 25000,
        "speed_kmh": (3, 6),
        "comments": [
            "Super randonnée 🌄",
            "Magnifique paysage",
            "Très belle balade",
            "Sortie montagne",
            "Randonnée entre amis"
        ]
    },

    "Marche": {
        "distance_min": 1000,
        "distance_max": 10000,
        "speed_kmh": (3, 5),
        "comments": [
            "Petite marche du soir",
            "Balade digestive",
            "Marche quotidienne",
            "Sortie détente"
        ]
    },

    "Natation": {
        "distance_min": 500,
        "distance_max": 5000,
        "speed_kmh": (2, 4),
        "comments": [
            "Bonne séance piscine 🏊",
            "Entraînement natation",
            "Séance technique",
            "Travail endurance"
        ]
    },

    "Escalade": {
        "distance_min": None,
        "distance_max": None,
        "speed_kmh": None,
        "comments": [
            "Séance bloc",
            "Très bonne grimpe 🧗",
            "Nouvelle voie validée",
            "Séance salle"
        ]
    }
}

# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()

# =========================================================
# CREATE TABLE
# =========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS activites_sportives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_salarie INTEGER NOT NULL,
    date_debut DATETIME NOT NULL,
    date_fin DATETIME NOT NULL,
    type_activite TEXT NOT NULL,
    distance_m INTEGER,
    temps_ecoule_s INTEGER,
    commentaire TEXT,
    source TEXT DEFAULT 'simulation_strava'
)
""")

conn.commit()

# =========================================================
# LOAD EMPLOYEES
# =========================================================

cursor.execute("""
SELECT id_salarie
FROM employes
""")

employees = cursor.fetchall()

print(f"{len(employees)} employés trouvés")

# =========================================================
# GENERATE ACTIVITIES
# =========================================================

total_inserted = 0

for employee in employees:

    id_salarie = employee[0]

    # Nombre d'activités aléatoire
    nb_activities = random.randint(
        NB_MIN_ACTIVITIES,
        NB_MAX_ACTIVITIES
    )

    for _ in range(nb_activities):

        # Choix sport
        sport_name = random.choice(list(SPORTS.keys()))

        sport = SPORTS[sport_name]

        # Date aléatoire sur 12 mois
        random_days = random.randint(0, 365)

        activity_date = TODAY - timedelta(days=random_days)

        # Heure réaliste
        activity_date = activity_date.replace(
            hour=random.randint(6, 21),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
            microsecond=0
        )

        # =================================================
        # DISTANCE / TEMPS
        # =================================================

        if sport_name == "Escalade":

            distance = None

            duration_sec = random.randint(1800, 10800)

        else:

            distance = random.randint(
                sport["distance_min"],
                sport["distance_max"]
            )

            speed = random.uniform(
                sport["speed_kmh"][0],
                sport["speed_kmh"][1]
            )

            duration_hours = (distance / 1000) / speed

            duration_sec = int(duration_hours * 3600)

        # =================================================
        # END DATE
        # =================================================

        end_date = activity_date + timedelta(
            seconds=duration_sec
        )

        # =================================================
        # COMMENT
        # =================================================

        comment = random.choice(
            sport["comments"]
        )

        # =================================================
        # INSERT
        # =================================================

        cursor.execute("""
        INSERT INTO activites_sportives (
            id_salarie,
            date_debut,
            date_fin,
            type_activite,
            distance_m,
            temps_ecoule_s,
            commentaire
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            id_salarie,
            activity_date.strftime("%Y-%m-%d %H:%M:%S"),
            end_date.strftime("%Y-%m-%d %H:%M:%S"),
            sport_name,
            distance,
            duration_sec,
            comment
        ))

        total_inserted += 1

# =========================================================
# SAVE
# =========================================================

conn.commit()

print(f"{total_inserted} activités générées")

# =========================================================
# EXAMPLE
# =========================================================

cursor.execute("""
SELECT *
FROM activites_sportives
ORDER BY RANDOM()
LIMIT 5
""")

rows = cursor.fetchall()

print("\nExemples d'activités :\n")

for row in rows:
    print(row)

# =========================================================
# CLOSE
# =========================================================

conn.close()

print("\nSimulation terminée avec succès")