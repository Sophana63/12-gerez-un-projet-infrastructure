import os

from dotenv import load_dotenv

load_dotenv()

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

DB_PATH = ROOT_DIR / "data" / "avantages_sportifs.db"

ADRESSE_ENTREPRISE = "1362 Av. des Platanes, 34970 Lattes"

DISTANCE_MAX_MARCHE_KM = 15
DISTANCE_MAX_VELO_KM = 25

PRIME_TAUX = 0.05

BIEN_ETRE_SEUIL_ACTIVITES = 15
BIEN_ETRE_JOURS = 5

GOOGLE_MAPS_API_KEY = os.getenv(
    "GOOGLE_MAPS_API_KEY",
    "test"
)