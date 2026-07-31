import csv
import glob
import re
import os
from app import create_app, db
from app.models import Ambulance
from app.Utils.locations import Locations

app = create_app()



def import_csv(csv_path):
	with open(csv_path, newline="", encoding="utf-8") as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			location_name = row['location']
			lat, lng = Locations[location_name]

			ambulance = Ambulance(
				name=row["incident_name"],
				location=row["location"],
				lat=lat,
				lon=lng,
				available_from=row["available_from"],
				vehicle_type=(row["vehicle_type"]),
				equipment_type=row["equipment_type"],
			)


        db.session.add(ambulance)

    db.session.commit()
        print(f"imported {csv_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with app.app_context():
        for path in sorted(glob.glob(os.path.join(script_dir, "Data_files", "ambulance_pool_*.csv"))):
            import_csv(path)
