import random
import requests

from app.config import GOOGLE_MAPS_API_KEY


def calculer_distance_google_maps(
    adresse_origine,
    adresse_destination,
    mode
):

    # ============================================
    # MODE TEST
    # ============================================

    if GOOGLE_MAPS_API_KEY == "test":

        return round(
            random.uniform(1.0, 30.0),
            1
        )

    # ============================================
    # GOOGLE MODE
    # ============================================

    mode_gmaps = {
        "vélo": "bicycling",
        "velo": "bicycling",
        "trottinette": "bicycling",
        "course": "walking",
        "running": "walking",
        "marche": "walking",
        "transport": "transit",
        "voiture": "driving",
    }.get(mode.lower(), "driving")

    url = (
        "https://maps.googleapis.com/maps/api/"
        "distancematrix/json"
    )

    params = {
        "origins": adresse_origine,
        "destinations": adresse_destination,
        "mode": mode_gmaps,
        "key": GOOGLE_MAPS_API_KEY,
        "language": "fr",
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:

            return None

        data = response.json()

        element = data["rows"][0]["elements"][0]

        if element["status"] == "OK":

            distance_metres = (
                element["distance"]["value"]
            )

            return round(
                distance_metres / 1000,
                2
            )

    except Exception as e:

        print(f"Erreur Google Maps : {e}")

    return None