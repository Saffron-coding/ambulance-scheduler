from datetime import datetime, timedelta
from app.utlis.distance import  get_eta, find_closest_ambulance

category_requirements = {
            "C1": {"equipment": ["ALS", "BLS"],
                   "vehicle": ["Rapid Response", "Double Crewed Ambulance"]},
            "C2": {"equipment": ["ALS", "BLS", "ILS"],
                   "vehicle": ["Rapid Response", "Double Crewed Ambulance"]},
            "C3": {"equipment": ["ALS", "BLS", "ILS"],
                   "vehicle": ["Rapid Response", "Double Crewed Ambulance", "Patient Transport Service"]},
            "C4": {"equipment": ["ALS", "BLS", "ILS"],
                   "vehicle": ["Rapid Response", "Double Crewed Ambulance", "Patient Transport Service"]},
        }

def priority_map(category):
    priority_map = {
        "C1": 1,
        "C2": 2,
        "C3": 3,
        "C4": 4
    }
    return priority_map.get(category, 99)

def parse_time(time_string):
    return datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")

def rules_met(job, ambulance, category_requirements):
    rule = category_requirements[job.user_assigned_category]
    if ambulance.equipment_level not in rule['equipment']:
        return False
    if ambulance.vehicle_type not in rule['vehicle']:
        return False
    return True


def run_scheduler(jobs, ambulances):
    scheduled_jobs = []
    unscheduled_jobs = []

    # Sort jobs by priority first, then by earliest call time
    sorted_jobs = sorted(
        jobs,
        key=lambda job: (priority_map(job.user_assigned_category), parse_time(job.call_time)))

    # Convert ambulance availability into datetime objects
    ambulance_state = []
    for ambulance in ambulances:
        ambulance_state.append({
            "ambulance": ambulance,
            "available_from": parse_time(ambulance.available_from)
        })

    #process each job
    for job in sorted_jobs:
        job_start = parse_time(job.call_time)
        #list of ambulances that can take this job
        candidate_ambulances = []

        for state in ambulance_state:
            if state["available_from"] <= job_start:
                ambulance = state["ambulance"]

                if rules_met(job, ambulance, category_requirements):
                    candidate_ambulances.append(ambulance)


#call API to decide which ambulance goes to which job based on distance
        best_ambulance, eta_minutes = find_closest_ambulance(
            job.lat,
            job.lon,
            candidate_ambulances)
        job_start = parse_time(job.call_time)
        if best_ambulance is None:
            #if no ambulance available
            unscheduled_jobs.append(job)
            continue
        job_duration = timedelta(minutes=eta_minutes + job.estimated_job_time)

        assigned = False

#keep this here
        for state in ambulance_state:
            if state["ambulance"] == best_ambulance and state["available_from"] <= job_start:
                scheduled_jobs.append({
                    "job": job,
                    "ambulance": state["ambulance"],
                    "assigned_start": job_start,
                    "assigned_end": job_start + job_duration,
                    "eta_minutes": eta_minutes
                })

                state["available_from"] = job_start + job_duration
                assigned = True
                break

        if not assigned:
            unscheduled_jobs.append(job)

    return scheduled_jobs, unscheduled_jobs