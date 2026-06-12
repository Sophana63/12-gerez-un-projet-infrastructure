import os
import requests

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv(
    "GOOGLE_MAPS_API_KEY"
)

url = (
    "https://maps.googleapis.com/maps/api/"
    "distancematrix/json"
)

params = {
    "origins": "Montpellier",
    "destinations": "Lattes",
    "mode": "walking",
    "key": API_KEY,
    "language": "fr",
}

response = requests.get(
    url,
    params=params
)

print("STATUS HTTP :")
print(response.status_code)

print("\nJSON :")
print(response.json())
