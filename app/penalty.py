from statistics import pstdev
from app.models import Allocation, Job

# ARP mean response-time targets (minutes) per category.
ARP_TARGET = {"C1": 7, "C2": 18, "C3": 120, "C4": 180}

# Category severity multipliers — a breach or drop on a higher-priority
# job costs more. Reused for both response-time weighting and unserved.
SEVERITY = {"C1": 4, "C2": 3, "C3": 2, "C4": 1}


def score_episode(episode_id, scheduler_type):
    """
    Compute the four raw penalty components for one episode under one
    scheduler. Returns them separately (not a weighted sum) so the
    sensitivity analysis can re-weight saved components later.
    """
    allocations = (Allocation.query
                   .join(Job, Allocation.job_id == Job.id)
                   .filter(Job.episode_id == episode_id,
                           Allocation.scheduler_type == scheduler_type)
                   .all())

    served_job_ids = {a.job_id for a in allocations}
    episode_jobs = Job.query.filter_by(episode_id=episode_id).all()

    # 1. Response time: category-weighted overage against ARP target.
    response_penalty = 0.0
    for a in allocations:
        job = Job.query.get(a.job_id)
        target = ARP_TARGET[job.user_assigned_category]
        overage = max(0.0, a.response_minutes - target)
        response_penalty += overage * SEVERITY[job.user_assigned_category]

    # 2. Unserved demand: severity-weighted count of jobs with no allocation.
    unserved_penalty = 0.0
    for job in episode_jobs:
        if job.id not in served_job_ids:
            unserved_penalty += SEVERITY[job.user_assigned_category]

    # 3. Workload fairness: spread of total busy minutes across units.
    busy_by_unit = {}
    for a in allocations:
        busy_by_unit[a.ambulance_id] = busy_by_unit.get(a.ambulance_id, 0.0) + a.total_job_minutes
    fairness_penalty = pstdev(busy_by_unit.values()) if len(busy_by_unit) > 1 else 0.0

    # 4. Equipment downgrade: sum of the per-allocation costs already stored.
    downgrade_penalty = sum(a.equipment_downgrade_cost for a in allocations)

    return {
        "response": response_penalty,
        "unserved": unserved_penalty,
        "fairness": fairness_penalty,
        "downgrade": downgrade_penalty,
    }