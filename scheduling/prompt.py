import os
import json
from anthropic import Anthropic
from app.Utils.distance import get_eta, find_closest_ambulance

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

MODEL = "claude-haiku-4-5"

# Equipment tiers, mirrored from the cost function so the prompt can show
# the LLM what each candidate's equipment means.
TIER = {"BLS": 0, "ILS": 1, "ALS": 2}
NEED = {"C1": 2, "C2": 1, "C3": 0, "C4": 0}


def _downgrade_cost(category, equipment_type):
    return max(0, TIER[equipment_type] - NEED[category])


def choose_ambulance(job, candidates):
    """
    Ask the LLM which of the feasible candidate units should serve this job.

    Returns (chosen_ambulance, eta_minutes, reason, is_fallback).
    On any failure (API error, unparseable reply, unit not in candidates)
    it falls back to nearest-ETA (greedy's choice) and flags it, so the
    fallback is recorded as a reliability event rather than silently
    becoming an agentic decision.
    """
    # Per-candidate facts — the same attributes greedy receives, surfaced
    # so the LLM can weigh them instead of collapsing to nearest.
    options = []
    for a in candidates:
        _, eta = get_eta(a.lat, a.lon, job.lat, job.lon)
        options.append({
            "id": a.id,
            "eta_minutes": round(eta, 1),
            "equipment_type": a.equipment_type,
            "downgrade_cost": _downgrade_cost(job.user_assigned_category, a.equipment_type),
        })

    prompt = (
        f"You are dispatching an ambulance for one emergency call.\n\n"
        f"Job category: {job.user_assigned_category} (already triaged, treat as correct)\n"
        f"Incident: {job.incident_name}\n\n"
        f"Candidate units (all are permitted to serve this job):\n"
        f"{json.dumps(options, indent=2)}\n\n"
        f"Lower eta_minutes is faster. downgrade_cost is how much scarce "
        f"capability is wasted by using this unit on this job (0 is ideal; "
        f"higher means a more capable unit is being spent on a job that "
        f"needs less).\n\n"
        f"Choose the single best unit, weighing response time against "
        f"wasted capability. Reply with ONLY a JSON object: "
        f'{{"ambulance_id": <id>, "reason": "<one sentence>"}}'
        f"Do not invent information not provided. "

    )

    try:
        msg = client.messages.create(
            model=MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        text = msg.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]  # take content between the fences
            if text.startswith("json"):
                text = text[4:]  # drop the "json" language tag
            text = text.strip()
        parsed = json.loads(text)
        chosen_id = parsed["ambulance_id"]
        reason = parsed.get("reason", "")

        chosen = next((a for a in candidates if a.id == chosen_id), None)
        if chosen is None:
            raise ValueError("LLM chose a unit not in candidates")

        _, eta = get_eta(chosen.lat, chosen.lon, job.lat, job.lon)
        return chosen, eta, reason, False
#use greedy if LLM fails
    except Exception as e:
        print("RAW LLM REPLY:", repr(msg.content[0].text))
        # Fallback: nearest eligible, flagged as a reliability event.
        chosen, eta = find_closest_ambulance(job.lat, job.lon, candidates)
        return chosen, eta, f"[fallback: {type(e).__name__}]", True