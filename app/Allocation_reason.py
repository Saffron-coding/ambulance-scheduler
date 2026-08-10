from app import db
from app.models import Allocation

TIER = {"BLS": 0, "ILS": 1, "ALS": 2}
NEED = {"C1": 2, "C2": 1, "C3": 0, "C4": 0}

def downgrade_cost(category, equipment_type):
    return max(0, TIER[equipment_type] - NEED[category])

def persist_allocations(rows, scheduler_type):
    for r in rows:
        db.session.add(Allocation(
            job_id=r["job"].id,
            ambulance_id=r["ambulance"].id,
            arrival_time=r["assigned_start"],
            clear_time=r["assigned_end"],
            response_minutes=r["response_minutes"],
            total_job_minutes=r["total_job_minutes"],
            equipment_downgrade_cost=r["equipment_downgrade_cost"],
            outcome="served",
            reason=r.get("reason", ""),
            scheduler_type=scheduler_type,
        ))
    db.session.commit()