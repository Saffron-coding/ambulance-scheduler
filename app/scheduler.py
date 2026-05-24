from datetime import datetime, timedelta

def priority_rank(category):
    priority_map = {
        "C1": 1,
        "C2": 2,
        "C3": 3,
        "C4": 4
    }
    return priority_map.get(category, 99)

def parse_time(time_string):
    return datetime.strptime(time_string, "%Y-%m-%d %H:%M")

def run_scheduler(jobs, ambulances):
    scheduled_jobs = []
    unscheduled_jobs = []

    # Sort jobs by priority first, then by earliest call time
    sorted_jobs = sorted(
        jobs,
        key=lambda job: (priority_rank(job.category), parse_time(job.call_time))
    )

    # Convert ambulance availability into datetime objects
    ambulance_state = []
    for ambulance in ambulances:
        ambulance_state.append({
            "ambulance": ambulance,
            "available_from": parse_time(ambulance.available_from)
        })
#call haversine formula to decide which ambulance goes to which job based on distance

    # Process each job in order
    for job in sorted_jobs:
        job_start = parse_time(job.call_time)
        job_duration = timedelta(minutes=job.total_job_minutes)

        assigned = False

        for state in ambulance_state:
            if state["available_from"] <= job_start:
                scheduled_jobs.append({
                    "job": job,
                    "ambulance": state["ambulance"],
                    "assigned_start": job_start,
                    "assigned_end": job_start + job_duration,
                    #"eta_minutes": eta_minutes
                })

                state["available_from"] = job_start + job_duration
                assigned = True
                break

        if not assigned:
            unscheduled_jobs.append(job)

    return scheduled_jobs, unscheduled_jobs
