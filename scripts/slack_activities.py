import os
import sqlite3
import random
import json
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "data" / "avantages_sportifs.db"

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

TEMPLATES = {
    "Course à pied": [
        "Bravo {prenom} {nom} ! Tu viens de courir {distance} km en {duree} min ! Quelle énergie ! {emojis}",
        "Quelle foulée {prenom} ! {distance} km parcourus, respect ! {emojis}",
    ],
    "Vélo": [
        "Super {prenom} {nom} ! {distance} km à vélo avalés en {duree} min ! {emojis}",
        "Ça roule fort {prenom} ! Belle sortie vélo de {distance} km ! {emojis}",
    ],
    "Randonnée": [
        "Magnifique {prenom} {nom} ! Une randonnée de {distance} km terminée ! {emojis}",
    ],
    "Natation": [
        "Splendide {prenom} {nom} ! {distance} km nagés en {duree} min ! {emojis}",
    ],
    "Escalade": [
        "Impressionnant {prenom} {nom} ! Belle session d'escalade de {duree} min ! {emojis}",
    ],
    "Yoga": [
        "Sérénité totale {prenom} {nom} ! {duree} min de yoga pour recharger les batteries ! {emojis}",
    ],
    "Marche": [
        "Bien joué {prenom} {nom} ! {distance} km de marche, chaque pas compte ! {emojis}",
    ],
}

EMOJIS = {
    "Course à pied": "🏃🔥💪",
    "Vélo": "🚴⚡👏",
    "Randonnée": "🥾🌄👏",
    "Natation": "🏊🌊💪",
    "Escalade": "🧗⛰️🔥",
    "Yoga": "🧘🌿✨",
    "Marche": "🚶👏🌞",
}

def send_slack_message(text: str):
    if not SLACK_WEBHOOK_URL:
        raise ValueError("SLACK_WEBHOOK_URL manquant")

    payload = json.dumps({"text": text}).encode("utf-8")

    req = urllib.request.Request(
        SLACK_WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req) as response:
        return response.read().decode("utf-8")

def format_activity(row):
    prenom = row["prenom"]
    nom = row["nom"]
    sport = row["type_activite"]
    distance = round((row["distance_m"] or 0) / 1000, 2)
    duree = round((row["temps_ecoule_s"] or 0) / 60)

    templates = TEMPLATES.get(
        sport,
        ["Bravo {prenom} {nom} ! Belle activité sportive réalisée en {duree} min ! {emojis}"]
    )

    template = random.choice(templates)

    return template.format(
        prenom=prenom,
        nom=nom,
        distance=distance,
        duree=duree,
        emojis=EMOJIS.get(sport, "👏💪")
    )

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
SELECT 
    a.id,
    a.date_debut,
    a.type_activite,
    a.distance_m,
    a.temps_ecoule_s,
    e.prenom,
    e.nom
FROM activites_sportives a
JOIN employes e ON e.id_salarie = a.id_salarie
ORDER BY a.date_debut DESC
LIMIT 10
""")

activities = cursor.fetchall()
conn.close()

messages = [format_activity(activity) for activity in activities]

slack_text = "🏆 *Dernières activités sportives des salariés*\n\n" + "\n".join(
    f"• {message}" for message in messages
)
print(slack_text)
send_slack_message(slack_text)

print("Messages Slack envoyés avec succès")