from faker import Faker
import random, csv
from app.utlis.locations import Locations
from app.models import Job

fake = Faker()
Faker.seed(42)
random.seed(42)

#poportions from NHS AQI March 2026
Category = (["C1"] * 5 +
            ["C2"] * 20 +
            ["C3"] * 15 +
            ["C4"] * 10)

random.shuffle(Category)

incident_name = ['cardiac arrest', 'respiratory failure', 'asthma attack', 'fall', 'heart-attack',
                 'chest pain', 'stomach pain', 'labour pains','stroke', 'dizziness', 'alcohol poisoning',
                 'unresponsive patient', 'seizure', 'concussion', 'Mental health crisis']

medical_history = ["Hypertension",
"Type 2 Diabetes Mellitus",
"Asthma","Chronic Obstructive Pulmonary Disease","Coronary Artery Disease","Atrial Fibrillation",
"Epilepsy", "Chronic Kidney Disease","Stroke", "Alzheimer’s Disease","Major Depressive Disorder","Generalised Anxiety Disorder",
"Peptic Ulcer Disease","Rheumatoid Arthritis", "Cardiac arrest", "Obesity", "Hypothyroidism",
"Hyperthyroidism","Iron Deficiency Anaemia","Deep Vein Thrombosis","Pulmonary Embolism",
"Breast Cancer", "Cirrhosis","Parkinson’s Disease","Sepsis"]

patient_notes= ["patient found on the floor unconscious", "patient not breathing",
                "Hypertension in a 58-year-old male", "diagnosed with anyeresm 10 years ago crushing chest pain",
                "treated with amlodipine and atorvastatin possible overdose",
                "Type 2 diabetes mellitus in a 62-year-old female light headed ",
                "Moderate persistent asthma in a 25-year-old male triggered by exercise",
                "Chronic obstructive pulmonary disease in a 70-year-old","Coronary artery disease in a 65-year-old male",
                "patient has numbness on right side of arm crush pain possible heart attack",
                "hard fall 28 patient complaining of possible arm break",
                "witness states patient is unable to breath","labour pain in female 8 months pregnant",
                "slurring words unable to communicate possible stroke",
                "cough blood 85 year old man","abdominal pain and vomiting possible alcohol poisoning",
                "Asthma attack, no inhaler struggling to breathe losing consciouness",
                "Anxiety disorder having a panic attack,suicidal thoughts","20 year seziure patient recorded history of eplipsy",
                "Collapsed in a gym unresponsive","confused 80 year old migranes and back pain",
                "high fever, cold, abdominal pain numbness in hands","severe burns accident with boiling ater patient by themselves",
                "stabbing pain in stomach,cannot move","no feeling in legs high fever and numbness in hands",
                ]
def generate_job(Category):
    location_name = random.choice(list(Locations.keys()))
    return {
        "incident_name": random.choice(incident_name),
        "user_assigned_category": Category,
        "system_assigned_category": "Pending",  # placeholder until system processes it
        "call_time": str(fake.date_time_this_year()),
        "time": str(fake.date_time_this_year()),
        "location": location_name,
        "lat": Locations[location_name][0],
        "lon": Locations[location_name][1],
        "patient_age": random.randint(18, 90),
        "patient_notes": random.choice(patient_notes),
        "medical_history": random.choice(medical_history),

    }

fieldnames = [ "incident_name", "user_assigned_category", "system_assigned_category",
              "call_time", "time", "location", "lat", "lon", "patient_age", "patient_notes",
              "medical_history"]

with open ("Ambulance_jobs.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for cat in Category:
        writer.writerow(generate_job(cat))




