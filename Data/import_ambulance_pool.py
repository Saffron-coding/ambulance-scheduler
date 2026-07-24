import csv
import glob
import re
import os
from app import create_app, db
from app.models import Ambulance
from app.Utils.locations import Locations

app = create_app()


def import_csv(csv_path):
    # derive episode id from filename, e.g. data/episode_003.csv -> 3
    match = re.search(r"episode_(\d+)", csv_path)
    episode_id = int(match.group(1)) if match else None


# ── write to CSV ──────────────────────────────────────────
def write_ambulances_csv(pool, path):
    open with(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:

        FOR EACH ambulance IN pool:
            write row = values of ambulance in FIELDNAMES order


    db.session.add(job)
    db.session.commit()
    print(f"imported {csv_path} (episode_id={episode_id})")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with app.app_context():
        for path in sorted(glob.glob(os.path.join(script_dir, "Data_files", "episode_*.csv"))):
            import_csv(path)
