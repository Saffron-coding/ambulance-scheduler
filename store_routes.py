from app.Utils.locations import Locations
from app.Utils.distance import get_eta
import time


def store_distances():
	count = 0
	for start_name, (start_lat, start_lon) in Locations.items():
		for end_name, (end_lat, end_lon) in Locations.items():
			if start_name == end_name:
				continue
			try:
				get_eta(start_lat, start_lon, end_lat, end_lon)
				count += 1
				print(count)
			except RuntimeError:
				print(f"stopped at count {count}: {start_name} - {end_name}")
				time.sleep(60)
				continue

if __name__ == "__main__":
	store_distances()
