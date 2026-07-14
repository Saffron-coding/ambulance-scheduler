"""Generate reproducible ambulance dispatch episodes with built-in contention.

Jobs are emitted in *clusters*: groups that are close in time, close in space,
and drawn from the same ambulance-eligibility pool (per ARP 2017 equipment
rules, C1/C2 compete for ALS-capable resources; C3/C4 can take any vehicle).
This forces the schedulers to make real trade-offs instead of trivially
serving scattered, non-competing jobs.

Difficulty knobs:
    --clustered-share    fraction of jobs placed in clusters (rest = background)
    --cluster-spread-min temporal tightness of each burst
    cluster_size         how many jobs compete at once
"""

import random
import csv
import argparse
import os
import math
from datetime import datetime, timedelta

from app.utlis.locations import Locations

# Fixed reference start so "07:00 on day 1" means the same thing in every
# episode; only offsets within the shift window vary by seed.
SHIFT_REFERENCE_START = datetime(2026, 3, 2, 7, 0, 0)

# NHS AQI proportions (C1:C2:C3:C4 = 5:20:15:10) — used for background jobs.
CATEGORY_WEIGHTS = {"C1": 5, "C2": 20, "C3": 15, "C4": 10}

# Eligibility pools per ARP 2017 equipment rules:
#   "als" -> C1/C2 jobs competing for ALS-capable resources
#   "any" -> C3/C4 jobs that any vehicle can serve

#each cluster has a 50% chance it will be from the als pool and 50% chance it will be C3 C4
POOL_SHARE = {"als": 0.5, "any": 0.5}
POOL_CATEGORY_WEIGHTS = {
#within the als cluster 20% will be C1 and 80% will be C2
    "als": {"C1": 0.2, "C2": 0.8},
#within the any cluster 60% will be C3 and 40% will be C4
    "any": {"C3": 0.6, "C4": 0.4},
}

# Incidents drawn per category so the free text the agentic scheduler sees is
# clinically coherent (no C4 cardiac arrests).
INCIDENTS_BY_CATEGORY = {
    "C1": ["cardiac arrest", "respiratory failure", "unresponsive patient"],
    "C2": ["heart-attack", "chest pain", "stroke", "asthma attack", "seizure"],
    "C3": ["fall", "labour pains", "alcohol poisoning", "concussion", "stomach pain"],
    "C4": ["dizziness", "stomach pain", "Mental health crisis"],
}

# Minutes. Duration increases as priority decreases: C1 crews treat fast and
# convey, while C3/C4 jobs tend toward longer see-and-treat episodes on scene.
# Swap in the category-dependent distributions from the seeding fix if they differ.
DURATION_RANGES_MIN = {
    "C1": (25, 60),
    "C2": (30, 75),
    "C3": (40, 100),
    "C4": (50, 130),
}

MEDICAL_HISTORY = ["Hypertension", "Type 2 Diabetes Mellitus", "Asthma",
                   "Chronic Obstructive Pulmonary Disease", "Coronary Artery Disease",
                   "Atrial Fibrillation", "Epilepsy", "Chronic Kidney Disease", "Stroke",
                   "Alzheimer's Disease", "Major Depressive Disorder", "Generalised Anxiety Disorder",
                   "Peptic Ulcer Disease", "Rheumatoid Arthritis", "Cardiac arrest", "Obesity",
                   "Hypothyroidism", "Hyperthyroidism", "Iron Deficiency Anaemia",
                   "Deep Vein Thrombosis", "Pulmonary Embolism", "Breast Cancer", "Cirrhosis",
                   "Parkinson's Disease", "Sepsis"]

patient_notes = ["patient found on the floor unconscious", "patient not breathing",
                 "Hypertension in a 58-year-old male",
                 "diagnosed with anyeresm 10 years ago crushing chest pain",
                 "treated with amlodipine and atorvastatin possible overdose",
                 "Type 2 diabetes mellitus in a 62-year-old female light headed",
                 "Moderate persistent asthma in a 25-year-old male triggered by exercise",
                 "Chronic obstructive pulmonary disease in a 70-year-old",
                 "Coronary artery disease in a 65-year-old male",
                 "patient has numbness on right side of arm crush pain possible heart attack",
                 "hard fall 28 patient complaining of possible arm break",
                 "witness states patient is unable to breath", "labour pain in female 8 months pregnant",
                 "slurring words unable to communicate possible stroke",
                 "cough blood 85 year old man", "abdominal pain and vomiting possible alcohol poisoning",
                 "Asthma attack, no inhaler struggling to breathe losing consciouness",
                 "Anxiety disorder having a panic attack, suicidal thoughts",
                 "20 year seziure patient recorded history of eplipsy",
                 "Collapsed in a gym unresponsive", "confused 80 year old migranes and back pain",
                 "high fever, cold, abdominal pain numbness in hands",
                 "severe burns accident with boiling water patient by themselves",
                 "stabbing pain in stomach, cannot move",
                 "no feeling in legs high fever and numbness in hands"]

fieldnames = ["episode_id", "incident_name", "user_assigned_category", "call_time",
              "location", "lat", "lon", "patient_age", "patient_notes",
              "medical_history", "estimated_job_time"]


def _haversine_km(a, b):
    """Straight-line fallback used ONLY for grouping nearby sites at generation
    time — this is not routing. For real drive distances, pass a distance_fn
    wrapping distance.py / the ORS route cache into generate_episode, e.g.:

        generate_episode(seed=1, distance_fn=lambda a, b: cached_route_km(a, b))

    where a and b are (lat, lon) tuples.
    """
#we use the haversine formula to calculate how far locations are from each other so that we can cluster jobs together
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))

#this function is a lookup table of what is near what
def _nearest_neighbours(k=4, distance_fn=_haversine_km):
    """name -> list of the k nearest other location names (precomputed once)."""
    names = list(Locations.keys())
    out = {}
#build a sorted list of four neighbours excluding the location the job in ascending order from the list of hardcoded 33 locations
    for name in names:
        others = sorted(
            (n for n in names if n != name),
            key=lambda n: distance_fn(Locations[name], Locations[n]),
        )
        out[name] = others[:k]
    return out


def _weighted_choice(weights_dict):
    keys = list(weights_dict)
    return random.choices(keys, weights=[weights_dict[k] for k in keys])[0]


def make_job(category, location_name, call_time):
    lo, hi = DURATION_RANGES_MIN[category]
    return {
        "incident_name": random.choice(INCIDENTS_BY_CATEGORY[category]),
        "user_assigned_category": category,
        "call_time": call_time,
        "location": location_name,
        "lat": Locations[location_name][0],
        "lon": Locations[location_name][1],
        "patient_age": random.randint(18, 90),
        "patient_notes": random.choice(patient_notes),
        "medical_history": random.choice(MEDICAL_HISTORY),
        "estimated_job_time": round(random.uniform(lo, hi), 2)
    }


def generate_episode(seed, num_jobs=50, shift_hours=8, clustered_share=0.7,
                     cluster_size=(3, 6), cluster_spread_min=20,
                     neighbour_k=4, distance_fn=_haversine_km,
                     shift_start=None, out_path=None):
    """
    Generate one reproducible episode as a time-ordered CSV of jobs.

    seed:               makes the episode fully reproducible
    num_jobs:           job volume (difficulty knob)
    clustered_share:    fraction of jobs emitted inside contention clusters
    cluster_size:       (min, max) jobs per cluster
    cluster_spread_min: std dev (minutes) of call times around a burst centre
    neighbour_k:        cluster jobs drawn from anchor + its k nearest sites
    distance_fn:        distance between two (lat, lon) tuples used for the
                        neighbour grouping; defaults to haversine, pass a
                        route-cache wrapper for real drive distances
    """
    random.seed(seed)
    shift_start = shift_start or SHIFT_REFERENCE_START
    shift_seconds = shift_hours * 3600
    neighbours = _nearest_neighbours(k=neighbour_k, distance_fn=distance_fn)
    names = list(Locations.keys())

    jobs = []

    # --- clustered jobs: same eligibility pool, nearby sites, tight time burst
    remaining = round(num_jobs * clustered_share)
    while remaining > 0:
        size = min(remaining, random.randint(*cluster_size))
        pool = _weighted_choice(POOL_SHARE)
        anchor = random.choice(names)
        candidate_locs = [anchor] + neighbours[anchor]
        centre = random.uniform(0, shift_seconds)
        for _ in range(size):
            cat = _weighted_choice(POOL_CATEGORY_WEIGHTS[pool])
            loc = random.choice(candidate_locs)
            t = min(max(random.gauss(centre, cluster_spread_min * 60), 0), shift_seconds)
            jobs.append(make_job(cat, loc, shift_start + timedelta(seconds=t)))
        remaining -= size

    # --- background jobs: uniform noise so clusters aren't the whole story
    for _ in range(num_jobs - len(jobs)):
        cat = _weighted_choice(CATEGORY_WEIGHTS)
        loc = random.choice(names)
        t = random.uniform(0, shift_seconds)
        jobs.append(make_job(cat, loc, shift_start + timedelta(seconds=t)))

    # sort by arrival so the CSV is a sequence, not a bag
    jobs.sort(key=lambda j: j["call_time"])
    for job in jobs:
        job["episode_id"] = seed  # seed uniquely identifies the episode
        job["call_time"] = job["call_time"].isoformat()

    out_path = out_path or f"episode_{seed:03d}.csv"
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(jobs)

    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate reproducible ambulance dispatch episodes with clustered contention.")
    parser.add_argument("--seeds", type=int, nargs="+", default=[1], help="one or more seeds, one episode each")
    parser.add_argument("--num-jobs", type=int, default=50)
    parser.add_argument("--shift-hours", type=int, default=8)
    parser.add_argument("--clustered-share", type=float, default=0.7,
                        help="fraction of jobs placed in contention clusters (0-1)")
    parser.add_argument("--cluster-spread-min", type=float, default=20,
                        help="temporal spread (std dev, minutes) of each cluster")
    parser.add_argument("--out-dir", type=str, default="Data")
    args = parser.parse_args()

    for s in args.seeds:
        path = generate_episode(seed=s, num_jobs=args.num_jobs, shift_hours=args.shift_hours,
                                clustered_share=args.clustered_share,
                                cluster_spread_min=args.cluster_spread_min,
                                out_path=f"{args.out_dir}/episode_{s:03d}.csv")
        print(f"wrote {path}")