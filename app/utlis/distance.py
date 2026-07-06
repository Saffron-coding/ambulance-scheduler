import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

# was hardcoded before — now read from env, never committed
API_key = os.environ["ORS_API_KEY"]

url = 'https://api.openrouteservice.org/v2/directions/driving-car'

headers = {
    'Authorization': API_key,
    'Content-Type': 'application/json'
}

# caching layer this is because I have 33 fixed locations to limit the number of API calls if api previous called check created cache folder
# 33 fixed locations means at most 33x33 unique ambulance->incident pairs,
# so a simple on-disk dict cache eliminates almost all repeat API calls
# across episodes and both schedulers.

CACHE_PATH = "cache/route_cache.json"
_cache = None  # loaded lazily, kept in memory for the life of the process


def _load_cache():
    global _cache
    if _cache is None:
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH) as f:
                _cache = json.load(f)
        else:
            _cache = {}
    return _cache

#this ensures that cached routes are saved and updated
def _save_cache():
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(_cache, f)


def _cache_key(start_lat, start_lon, end_lat, end_lon):
    # JSON keys must be strings, so build a stable string key from the coordinate pair
    return f"{start_lat},{start_lon},{end_lat},{end_lon}"


def get_eta(start_lat, start_lon, end_lat, end_lon):
    cache = _load_cache()
    key = _cache_key(start_lat, start_lon, end_lat, end_lon)

    if key in cache:
        distance_miles, eta_minutes = cache[key]
        return distance_miles, eta_minutes

    payload = {
        "coordinates": [
            [start_lon, start_lat],
            [end_lon, end_lat]
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
# this is because API has a limit on the number of calls this should not be hit as we are storing the number of repeat calls
    if response.status_code == 429:
        raise RuntimeError("OpenRouteService rate limit hit — check cache is being used and/or slow down requests")
    response.raise_for_status()

    data = response.json()

    distance_metres = data["routes"][0]["summary"]["distance"]
    duration_seconds = data["routes"][0]["summary"]["duration"]

    distance_miles = round(distance_metres / 1609.34, 2)
    eta_minutes = round(duration_seconds / 60, 1)

    cache[key] = (distance_miles, eta_minutes)
    _save_cache()

    return distance_miles, eta_minutes


# this finds the closest ambulance after being filtered - find closest for my job
def find_closest_ambulance(incident_lat, incident_lon, candidate_ambulances):
    # candidate_ambulances is in scheduler and is created by the filter - ambulances available after filter rules
    if candidate_ambulances is None:
        candidate_ambulances = []

    ranked = []
    for ambulance in candidate_ambulances:
        distance_miles, eta_minutes = get_eta(ambulance.lat, ambulance.lon, incident_lat, incident_lon)
        ranked.append((ambulance, distance_miles, eta_minutes))
    # sorts ambulances shortest ETA to longest ETA
    ranked.sort(key=lambda x: x[2])

    if len(ranked) == 0:
        return None, None

    best_ambulance = ranked[0][0]
    best_eta = ranked[0][2]

    return best_ambulance, best_eta