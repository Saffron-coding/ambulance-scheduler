from datetime import *
import heapq
from itertools import count
from app.Utils.distance import  get_eta, find_closest_ambulance
from app.Allocation_reason import persist_allocations, downgrade_cost
from app.models import Allocation
from app import db

Schedule_type = 'greedy'

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
    priority_map = {
        "C1": 1,
        "C2": 2,
        "C3": 3,
        "C4": 4
    }
    return priority_map.get(category, 99)

def rules_met(job, ambulance, category_requirements):
    rule = category_requirements[job.user_assigned_category]
    if ambulance.equipment_type not in rule['equipment']:
        return False
    if ambulance.vehicle_type not in rule['vehicle']:
        return False
    return True

"""
    Event-driven scheduler.

    This scheduler only ever lets a job influence a decision once
    its own call_time has passed, and only reconsiders ambulances at the
    moment they actually become free (or a new job arrives) - the two kinds
    of "events" in the simulation.

    Jobs that arrive but find nothing eligible free go into a priority
    queue (`pending`) and get retried every time an ambulance frees up or
    another job arrives, instead of being marked unscheduled immediately.
        """

def run_scheduler(jobs, ambulances):
    Allocation.query.filter_by(scheduler_type="greedy").delete()
    db.session.commit()
    horizon = SHIFT_REFERENCE_START + timedelta(hours=8)

    scheduled_jobs = []
    unscheduled_jobs = []
# loop through every ambulance and create an ambulance state including ambulance.id and available time
    ambulance_state = {
        ambulance.id: {"ambulance": ambulance, "available_from": ambulance.available_from}
        for ambulance in ambulances
    }
#arrivals hold the entire job data indexed
    arrivals = sorted(jobs, key=lambda job: job.call_time)
    arrival_idx = 0
#tie is a way of assigning a ticket number per ambulance job so that if it looks the same as another there is a tie
    tie = count()
    pending = []  # heap of (priority, call_time, tie, job) - jobs waiting for an ambulance

    # seed the event queue with every job arrival and every ambulance's
    # initial availability; assignments push new "free" events as they happen
    #events list is dynamic continuously updating as ambulances free up
    events = []  # heap of (time, tie, kind)
    for job in arrivals:
        #this takes my heap of events and adds job call time with the top always being the earliest value
        heapq.heappush(events, (job.call_time, next(tie), "arrival"))

    for state in ambulance_state.values():
        heapq.heappush(events, (state["available_from"], next(tie), "free"))
#evaluates whether I can assign waiting jobs
    def try_match(now):
#are there any ambulances available now
        free_ambulances = [
            state["ambulance"] for state in ambulance_state.values()
            if state["available_from"] <= now
        ]
#if no free ambulances or no pending jobs do nothing
        if not free_ambulances or not pending:
            return

        held = []
        while pending and free_ambulances:
            priority, call_time, _, job = heapq.heappop(pending)
            candidates = [a for a in free_ambulances if rules_met(job, a, category_requirements)]
            best_ambulance, eta_minutes = find_closest_ambulance(job.lat, job.lon, candidates)

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
            })

            ambulance_state[best_ambulance.id]["available_from"] = job_end
#instead of checking every minute a future event is created stating the time an ambulance will be free
            heapq.heappush(events, (job_end, next(tie), "free"))
#
            free_ambulances = [a for a in free_ambulances if a.id != best_ambulance.id]

        for priority, call_time, job in held:
            heapq.heappush(pending, (priority, call_time, next(tie), job))

    while events and events[0][0] <= horizon:
        now = events[0][0]

        # pull every event sharing this exact timestamp (e.g. several calls
        # arriving at once, or a call landing the same instant an ambulance
        # frees up) into `pending` before matching anything, so simultaneous
        # arrivals are decided by (priority, call_time) - not by whatever
        # order they happened to pop off `events` in
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

    # anything still waiting once every arrival and every ambulance free-up
    # store any remaining unscheduled jobs only hold job data
    unscheduled_jobs = [job for *_, job in pending]
#save scheduled jobs to allocation table
    persist_allocations(scheduled_jobs, "greedy")

    return scheduled_jobs, unscheduled_jobs