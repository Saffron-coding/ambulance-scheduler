import csv
from app import create_app, db
from app.models import Job

app = create_app()

def import_csv():
    with app.app_context():
        with open("data/ambulance_jobs_synthetic_150.csv", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                existing_job = Job.query.filter_by(job_id=row["job_id"]).first()
                if existing_job:
                    continue

                job = Job(
                    job_id=row["job_id"],
                    category=row["category"],
                    call_time=row["call_time"],
                    dispatch_time=row["dispatch_time"],
                    arrival_time=row["arrival_time"],
                    clear_time=row["clear_time"],
                    response_minutes=float(row["response_minutes"]),
                    service_minutes=float(row["service_minutes"]),
                    total_job_minutes=float(row["total_job_minutes"]),
                    location=row["location"],
                    outcome=row["outcome"]
                )

                db.session.add(job)

            db.session.commit()
            print("CSV data imported successfully.")

if __name__ == "__main__":
    import_csv()