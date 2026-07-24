"""Fleet construction for ambulance pool

Builds the starting ambulance pool: each unit in COMPOSITION is assigned a
distinct home base drawn from the location set, using an isolated, seeded RNG
so the layout is reproducible and independent of any other random draws in
the process (job generation, tie-breaking, etc.).
"""
import random
from dataclasses import dataclass
from datetime import datetime

# Draft 12-unit fleet. (vehicle_type, equipment_level)
# Vehicle type encodes job eligibility only, not speed.
COMPOSITION: list[tuple[str, str]] = [
    ("RRV", "ALS"), ("RRV", "ALS"), ("RRV", "ALS"),
    ("DCA", "ALS"), ("DCA", "ALS"), ("DCA", "ALS"),
    ("DCA", "BLS"), ("DCA", "BLS"),
    ("DCA", "ILS"), ("DCA", "ILS"),
    ("PTS", "BLS"), ("PTS", "BLS"),
]

@dataclass
class Ambulance:
    """A single unit.

    `home_*` is the station the unit returns to after completing a job;
    `current_*` is where it actually is. Under a return-to-base policy the two
    coincide whenever the unit is idle. Swap this class out for the SQLAlchemy
    model if the pool is persisted rather than held in memory.
    """

    id: str
    base: str
    home_lat: float
    home_lon: float
    equipment_level: str
    vehicle_type: str
    available_from: datetime

    def __post_init__(self) -> None:
        self.current_lat = self.home_lat
        self.current_lon = self.home_lon


def make_ambulance(
    ambulance_id: str,
    base: str,
    lat: float,
    lon: float,
    equipment_level: str,
    vehicle_type: str,
    available_from: datetime
) -> Ambulance:
    return Ambulance(
        id=ambulance_id,
        base=base,
        home_lat=lat,
        home_lon=lon,
        equipment_level=equipment_level,
        vehicle_type=vehicle_type,
        available_from=available_from
    )

def build_ambulance_pool(locations, composition, seed):
    random.seed(seed)
    names = sorted(locations)
    bases = random.sample(names, k=len(composition))

    pool = []
    for i, (base, (vehicle_type, equipment_level)) in enumerate(zip(bases, composition)):
        lat, lon = locations[base]
        pool.append(Ambulance(f"AMB_{i:02d}", base, lat, lon, equipment_level, vehicle_type))
    return pool


