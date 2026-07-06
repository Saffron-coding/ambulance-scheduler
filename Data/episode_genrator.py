from faker import Faker
import random, csv, argparse
from datetime import timedelta
from app.utlis.locations import Locations

incident_name = ['cardiac arrest', 'respiratory failure', 'asthma attack', 'fall', 'heart-attack',
                 'chest pain', 'stomach pain', 'labour pains', 'stroke', 'dizziness', 'alcohol poisoning',
                 'unresponsive patient', 'seizure', 'concussion', 'Mental health crisis']

medical_history = ["Hypertension", "Type 2 Diabetes Mellitus", "Asthma",
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
                  "Type 2 diabetes mellitus in a 62-year-old female light headed ",
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

fieldnames = ["incident_name", "user_assigned_category",
              "call_time", "location", "lat", "lon", "patient_age", "patient_notes",
              "medical_history"]

DEFAULT_CATEGORY_WEIGHTS = {"C1": 5, "C2": 20, "C3": 15, "C4": 10}  # NHS AQI March 2026 proportions


def build_category_list(category_weights, num_jobs):
    """Scale the weight proportions to num_jobs and shuffle."""
    total_weight = sum(category_weights.values())
    categories = []
    for cat, weight in category_weights.items():
        count = round(num_jobs * weight / total_weight)
        categories += [cat] * count
    # rounding can leave us a job or two short/long of num_jobs; pad or trim
    while len(categories) < num_jobs:
        categories.append(random.choice(list(category_weights)))
    categories = categories[:num_jobs]
    random.shuffle(categories)
    return categories


def generate_job(fake, category):
    location_name = random.choice(list(Locations.keys()))
    return {
        "incident_name": random.choice(incident_name),
        "user_assigned_category": category,
        "location": location_name,
        "lat": Locations[location_name][0],
        "lon": Locations[location_name][1],
        "patient_age": random.randint(18, 90),
        "patient_notes": random.choice(patient_notes),
        "medical_history": random.choice(medical_history),
    }


def generate_episode(seed, num_jobs=50, category_weights=None, shift_hours=8, shift_start=None, out_path=None):
    """
    Generate one reproducible episode: a bounded, time-ordered sequence of jobs
    plus the fleet-state reset happens separately, in the scheduler/runner, not here.

    seed:              int, makes the episode fully reproducible
    num_jobs:          job volume for this episode (difficulty knob)
    category_weights:  dict like {"C1": 5, "C2": 20, ...}; proportions, not literal counts
    shift_hours:       length of the shift window call_times are drawn within
    shift_start:       datetime; defaults to a fixed reference so episodes are comparable
    out_path:          CSV path to write; defaults to episode_{seed:03d}.csv
    """
    fake = Faker()
    Faker.seed(seed)
    random.seed(seed)

    category_weights = category_weights or DEFAULT_CATEGORY_WEIGHTS
    categories = build_category_list(category_weights, num_jobs)

    if shift_start is None:
        # fixed reference start so "9am on day 1" means the same thing across episodes;
        # only the offsets within the window vary by seed
        shift_start = fake.date_time_this_year().replace(hour=7, minute=0, second=0, microsecond=0)

    jobs = []
    for cat in categories:
        job = generate_job(fake, cat)
        offset_seconds = random.uniform(0, shift_hours * 3600)
        job["call_time"] = str(shift_start + timedelta(seconds=offset_seconds))
        jobs.append(job)

    # sort so the CSV reflects arrival order — this is what makes it a sequence, not a bag
    jobs.sort(key=lambda j: j["call_time"])

    out_path = out_path or f"episode_{seed:03d}.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for job in jobs:
            writer.writerow(job)

    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate reproducible ambulance dispatch episodes.")
    parser.add_argument("--seeds", type=int, nargs="+", default=[1], help="one or more seeds, one episode each")
    parser.add_argument("--num-jobs", type=int, default=50)
    parser.add_argument("--shift-hours", type=int, default=8)
    parser.add_argument("--out-dir", type=str, default="data")
    args = parser.parse_args()

    for s in args.seeds:
        path = generate_episode(seed=s, num_jobs=args.num_jobs, shift_hours=args.shift_hours,
                                 out_path=f"{args.out_dir}/episode_{s:03d}.csv")
        print(f"wrote {path}")