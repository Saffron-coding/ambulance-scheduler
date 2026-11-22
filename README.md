# LLM Agent vs Rule-Based Ambulance Dispatch

MSc Computer Science dissertation, University of Birmingham (2026). Awarded 74% (Distinction).

An event-driven simulation that compares an **LLM dispatch agent** (Anthropic API) with a **greedy rule-based scheduler** for allocating ambulances to emergency calls. Both schedulers see the same live fleet information and make one decision per job. Only the decision-maker changes, so the two can be compared fairly.

## Why

Ambulance services have a limited fleet. Each decision trades off response time, fairness across crews and whether the right equipment gets to the patient. Rule-based dispatch is fast and predictable but rigid. This project tests whether an LLM agent can make better trade-offs, and how reliable it is when it has to work within hard operational constraints.

## How it works

- **Event-driven simulation:** an event queue processes job arrivals and units becoming free. Jobs that arrive together are queued by priority (ARP category C1–C4) and call time. Jobs with no eligible unit are retried, not dropped. There is no lookahead, so decisions use only present-tense fleet state.
- **Greedy scheduler** (`scheduling/greedy_based_scheduler.py`): assigns the nearest eligible unit by ETA.
- **LLM agent** (`scheduling/agentic_scheduler.py`, `scheduling/prompt.py`): sends the job and its feasible candidate units to Claude through a prompt template, then parses the reply into a structured allocation. If the API call fails, the reply can't be parsed or the chosen unit isn't a valid candidate, it falls back to the greedy choice and logs this as a reliability event.
- **Hard constraints:** equipment eligibility and unit availability are checked before any decision is accepted. Neither scheduler can make an infeasible allocation.
- **Routing:** travel times across 33 Birmingham locations come from the OpenRouteService API and are cached as JSON to avoid repeat calls.

## Evaluation

Both schedulers write to one shared `allocation` table, and the scorer reads only that table. Each episode is scored with a four-part penalty function (`app/penalty.py`):

| Component | What it penalises |
|---|---|
| Response time | Lateness against NHS ARP targets, weighted by category |
| Unserved demand | Jobs still waiting at the end of the episode |
| Workload fairness | Uneven distribution of work across units |
| Equipment downgrade | Sending a lower-capability unit than the category needs |

Results are compared across 15 seeded episodes using a paired Wilcoxon signed-rank test, with effect size and win rate. LLM fallbacks are reported separately as a reliability measure.

## Results

whilst the agentic scheduler preformed better than the rule based deterministic scheduler this was not because it served more jobs or was exponetially faster this is because it was able to balance work load and was able to preform equipment matching to a higher degree than the deterministic system. 

## Tech stack

Python, Flask, PostgreSQL, SQLAlchemy, Flask-Migrate, Anthropic API, OpenRouteService API, Jinja2, Chart.js

## Project structure

```
app/            Flask app: models, routes, penalty scoring, templates
scheduling/     Greedy scheduler, LLM agent and prompt template
Data/           Episode generator, fleet and job import scripts, generated CSVs
migrations/     Database migrations (Flask-Migrate)
store_routes.py Pre-builds the OpenRouteService route cache
results.json    Scored results per episode and scheduler
```

## Running locally

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Create a `.env` file:
   ```
   DATABASE_URI=postgresql://localhost:5432/ambulance_db
   ANTHROPIC_API_KEY=your-key
   ORS_API_KEY=your-key
   SECRET_KEY=any-string
   ```
3. Set up the database: `flask db upgrade`
4. Load the fleet and episodes
5. Build the route cache (once): `python store_routes.py`
6. Run the app: `python run.py`

To switch scheduler, change the scheduler import in `app/routes.py`.

## Data

All job data is synthetic. The source NHS Ambulance Quality Indicators give aggregate statistics rather than individual incidents, so `Data/episode_generator.py` creates seeded, reproducible job-level episodes with category mix and clustering proportional to those statistics.

## Limitations

- One unit is sent per job. Real C1 practice often sends a rapid-response vehicle plus an ambulance as backup.
- Travel times are the same for all vehicle types. Vehicle type only decides which jobs a unit can serve.
- The data is synthetic, so the results show how the schedulers compare with each other, not how they would perform in a real service.
- Chart.js

