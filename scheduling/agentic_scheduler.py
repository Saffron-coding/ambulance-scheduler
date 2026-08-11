from datetime import *
import heapq
from itertools import count
from app.Utils.distance import get_eta, find_closest_ambulance
from app.Allocation_reason import persist_allocations, downgrade_cost
from app.models import Allocation
from app import db
from scheduling.prompt import choose_ambulance

SHIFT_REFERENCE_START = datetime(2026, 3, 2, 8, 0, 0)

category_requirements = {
    "C1": {"equipment": ["ALS"],
           "vehicle": ["Rapid Response", "Double Crewed Ambulance"]},
    "C2": {"equipment": ["ALS", "ILS"],
           "vehicle": ["Rapid Response", "Double Crewed Ambulance"]},
    "C3": {"equipment": ["ALS", "BLS", "ILS"],
           "vehicle": ["Rapid Response", "Double Crewed Ambulance", "Patient Transport Service"]},
    "C4": {"equipment": ["ALS", "BLS", "ILS"],
           "vehicle": ["Rapid Response", "Double Crewed Ambulance", "Patient Transport Service"]},
}


def priority_map(category):
    return {"C1": 1, "C2": 2, "C3": 3, "C4": 4}.get(category, 99)


def rules_met(job, ambulance, category_requirements):
    rule = category_requirements[job.user_assigned_category]
    if ambulance.equipment_type not in rule['equipment']:
        return False
    if ambulance.vehicle_type not in rule['vehicle']:
        return False
    return True


def run_scheduler(jobs, ambulances):
    Allocation.query.filter_by(scheduler_type="agentic").delete()
    db.session.commit()
    horizon = SHIFT_REFERENCE_START + timedelta(hours=8)

    scheduled_jobs = []
    unscheduled_jobs = []

    ambulance_state = {
        ambulance.id: {"ambulance": ambulance, "available_from": ambulance.available_from}
        for ambulance in ambulances
    }

    arrivals = sorted(jobs, key=lambda job: job.call_time)
    arrival_idx = 0
    tie = count()
    pending = []

    events = []
    for job in arrivals:
        heapq.heappush(events, (job.call_time, next(tie), "arrival"))
    for state in ambulance_state.values():
        heapq.heappush(events, (state["available_from"], next(tie), "free"))

    def try_match(now):
        free_ambulances = [
            state["ambulance"] for state in ambulance_state.values()
            if state["available_from"] <= now
        ]
        if not free_ambulances or not pending:
            return

        held = []
        while pending and free_ambulances:
            priority, call_time, _, job = heapq.heappop(pending)
            candidates = [a for a in free_ambulances if rules_met(job, a, category_requirements)]

            if not candidates:
                held.append((priority, call_time, job))
                continue

            # THE ONLY DIFFERENCE FROM GREEDY: the LLM picks the unit.
            best_ambulance, eta_minutes, reason, is_fallback = choose_ambulance(job, candidates)

            if best_ambulance is None:
                held.append((priority, call_time, job))
                continue

            job_duration = timedelta(minutes=eta_minutes + job.estimated_job_time)
            job_end = now + job_duration
            scheduled_jobs.append({
                "job": job,
                "ambulance": best_ambulance,
                "assigned_start": now,
                "assigned_end": job_end,
                "eta_minutes": eta_minutes,
                "response_minutes": eta_minutes + (now - job.call_time).total_seconds() / 60,
                "total_job_minutes": eta_minutes + job.estimated_job_time,
                "equipment_downgrade_cost": downgrade_cost(job.user_assigned_category, best_ambulance.equipment_type),
                "reason": reason,
                "is_fallback": is_fallback,
            })

            ambulance_state[best_ambulance.id]["available_from"] = job_end
            heapq.heappush(events, (job_end, next(tie), "free"))
            free_ambulances = [a for a in free_ambulances if a.id != best_ambulance.id]

        for priority, call_time, job in held:
            heapq.heappush(pending, (priority, call_time, next(tie), job))

    while events and events[0][0] <= horizon:
        now = events[0][0]
        while events and events[0][0] == now:
            _, _, kind = heapq.heappop(events)
            if kind == "arrival":
                job = arrivals[arrival_idx]
                arrival_idx += 1
                heapq.heappush(
                    pending,
                    (priority_map(job.user_assigned_category), job.call_time, next(tie), job)
                )
        try_match(now)

    unscheduled_jobs = [job for *_, job in pending]

    persist_allocations(scheduled_jobs, "agentic")

    return scheduled_jobs, unscheduled_jobs