import csv
import glob
import re
from app import create_app, db
from app.models import Job
from datetime import datetime
from app.utlis.locations import Locations

app = create_app()


def import_csv(csv_path):
    # derive episode id from filename, e.g. data/episode_003.csv -> 3
    match = re.search(r"episode_(\d+)", csv_path)
    episode_id = int(match.group(1)) if match else None

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            location_name = row['location']
            lat, lng = Locations[location_name]

            job = Job(
                    episode_id=episode_id,
                    incident_name=row["incident_name"],
                    location=row["location"],
                    lat=lat,
                    lon=lng,
                    user_assigned_category=row["user_assigned_category"],
                    call_time= datetime.strptime(row["call_time"],"%Y-%m-%d %H:%M:%S.%f"),
                    patient_age=int(row["patient_age"]),
                    medical_history=row["medical_history"],
                    patient_notes=row["patient_notes"]
                )

            db.session.add(job)

    db.session.commit()
    print(f"imported {csv_path} (episode_id={episode_id})")


if __name__ == "__main__":
    with app.app_context():
        for path in sorted(glob.glob("data/episode_*.csv")):
            import_csv(path)