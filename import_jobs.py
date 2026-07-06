import csv
from app import create_app, db
from app.models import Job
from datetime import datetime
from app.routes import escalate_priority
from app.utlis.locations import Locations

app = create_app()

def import_csv():
    with app.app_context():
        with open("data/ambulance_jobs.csv", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                location_name = row['location']
                lat, lng = Locations[location_name]

                escalated_category = escalate_priority(
                    row['user_assigned_category'],
                    row['incident_name'],
                    row['medical_history'],
                    row['patient_notes'],
                    int(row['patient_age']),
                )
                job = Job(
                        incident_name=row["incident_name"],
                        location=row["location"],
                        lat=lat,
                        lon=lng,
                        user_assigned_category=row["user_assigned_category"],
                        system_assigned_category=escalated_category,
                        call_time= datetime.strptime(row["call_time"],"%Y-%m-%d %H:%M:%S.%f"),
                        time=datetime.strptime(row["time"],"%Y-%m-%d %H:%M:%S.%f"),
                        patient_age=int(row["patient_age"]),
                        medical_history=row["medical_history"],
                        patient_notes=row["patient_notes"]
                    )

                db.session.add(job)

            db.session.commit()
            print("CSV data imported successfully.")

if __name__ == "__main__":
    import_csv()