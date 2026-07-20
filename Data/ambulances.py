"""Generate reproducible ambulance fleet of fixed 12 ambulances that will be resourced against 50 ambulance jobs
this is a scaled version of the real life operational constraint that occurs with WMAS operating 460 ambulances a day"""
#I need to decide what portion of ambulance have what equipment and vehicle type ratio must be in-line with NHS statistics


import random
import csv
import argparse
import os
import math
from datetime import datetime, timedelta
from app.Utils.locations import Locations

# ══════════════════════════════════════════════════════════
# AMBULANCE POOL GENERATOR  — run once, produces ambulances.csv
# Static reference data: no episode_id, no timestamps.
# ══════════════════════════════════════════════════════════

from app.Utils import locations           # {name: (lat, lon)} — your 33 fixed Birmingham sites

CONSTANTS:
    SEED        = 42
    OUTPUT_CSV  = "Data/ambulances.csv"
    FIELDNAMES  = [ambulance_id, home_base, lat, lon, equipment, vehicle_type]

    # Fixed fleet mix as (vehicle_type, equipment) pairs — sums to 12.
    # Set explicitly so the proportions are a justifiable modelling choice.
    FLEET_COMPOSITION = [
        (Rapid Response,            ALS)   ×3
        (Double Crewed Ambulance,   ALS)   ×3
        (Double Crewed Ambulance,   BLS)   ×2
        (Double Crewed Ambulance,   ILS)   ×2
        (Patient Transport Service, BLS)   ×2
    ]

    # Your scheduler.py table — reused ONLY to sanity-check coverage.
    CATEGORY_REQUIREMENTS = {
        C1: equipment ∈ {ALS, BLS},       vehicle ∈ {RRV, DCA}
        C2: equipment ∈ {ALS, BLS, ILS},  vehicle ∈ {RRV, DCA}
        C3: equipment ∈ {ALS, BLS, ILS},  vehicle ∈ {RRV, DCA, PTS}
        C4: equipment ∈ {ALS, BLS, ILS},  vehicle ∈ {RRV, DCA, PTS}
    }


# ── build one ambulance record (one CSV row) ──────────────
FUNCTION make_ambulance(ambulance_id, home_base, lat, lon, equipment, vehicle_type):
    RETURN record {
        ambulance_id, home_base, lat, lon, equipment, vehicle_type
    }


# ── build the pool of 12 (seeded, reproducible) ───────────
FUNCTION build_ambulance_pool(Locations, composition, seed):
    rng   ← seeded_rng(seed)                       # isolated generator
    names ← sort( keys of Locations )              # stable order before sampling
    bases ← rng.sample(names, size = length(composition))   # distinct home locations

    pool ← empty list
    FOR i FROM 0 TO length(composition) - 1:
        base                    ← bases[i]
        (vehicle_type, equip)   ← composition[i]
        (lat, lon)              ← Locations[base]   # coords from your dict
        id                      ← "AMB_" + zero_pad(i, 2)
        pool.append( make_ambulance(id, base, lat, lon, equip, vehicle_type) )

    RETURN pool


# ── write to CSV ──────────────────────────────────────────
FUNCTION write_ambulances_csv(pool, path):
    OPEN path FOR writing:
        write header row  = FIELDNAMES
        FOR EACH ambulance IN pool:
            write row = values of ambulance in FIELDNAMES order


# ── feasibility check: every category must have ≥1 unit ───
FUNCTION coverage_report(pool):
    FOR EACH (category, req) IN CATEGORY_REQUIREMENTS:
        eligible ← count units a IN pool WHERE
                       a.equipment    ∈ req.equipment
                   AND a.vehicle_type ∈ req.vehicle
        PRINT category, eligible
        ASSERT eligible > 0        # else those jobs are unservable → penalty noise


# ── main (run once) ───────────────────────────────────────
MAIN:
    pool ← build_ambulance_pool(Locations, FLEET_COMPOSITION, SEED)
    write_ambulances_csv(pool, OUTPUT_CSV)
    coverage_report(pool)



