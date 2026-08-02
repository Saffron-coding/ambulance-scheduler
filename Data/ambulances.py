import csv
import random
from datetime import datetime
from app.Utils.locations import Locations

FLEET = [
    ("Rapid Response", "ALS"),
    ("Rapid Response", "ALS"),
    ("Rapid Response", "ALS"),
    ("Double Crewed Ambulance", "ALS"),
    ("Double Crewed Ambulance", "ALS"),
    ("Double Crewed Ambulance", "ALS"),
    ("Double Crewed Ambulance", "BLS"),
    ("Double Crewed AmbulanceA", "BLS"),
    ("Double Crewed Ambulance", "ILS"),
    ("Double Crewed Ambulance", "ILS"),
    ("Patient Transport Service", "BLS"),
    ("Patient Transport Service", "BLS"),
]

available_from = datetime(2026, 1, 1, 8, 0, 0)

bases = random.sample(list(Locations), len(FLEET))

rows = []
for i, ((vehicle_type, equipment_type), base) in enumerate(zip(FLEET, bases), start=1):
    lat, lon = Locations[base]
    rows.append({
        "id": i,
        "name": f"AMB{i:02d}",
        "location": base,
        "lat": lat,
        "lon": lon,
        "available_from": available_from.isoformat(),
        "vehicle_type": vehicle_type,
        "equipment_type": equipment_type,
    })

with open("Data_files/ambulances.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "id", "name", "location", "lat", "lon",
        "available_from", "vehicle_type", "equipment_type",
    ])
    writer.writeheader()
    writer.writerows(rows)