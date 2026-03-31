A web application for managing ambulance jobs and simulating scheduling decisions based on priority and availability.



 Overview

The Ambulance Scheduler allows users to:

- Create, view, update, and delete ambulance jobs
- Manage ambulance resources
- Run a scheduling algorithm to assign jobs to available ambulances

The system is designed to simulate real-world dispatch scenarios.

The dataset used for the application was synthetically created using patterns derived from NHS Ambulance Quality indicator data.
The source data provides operational statistics rather than record level incidents so a job-level dataset was created to simulate 
realistic ambulance scheduling scenarios



 Features

- Job management (CRUD)
- Ambulance management
- Scheduling system (greedy algorithm)
- Priority-based job sorting (C1, C2, C3, C4)
- Dashboard and navigation UI
- Chart.js visualisation of scheduling results



 Scheduling Logic

The system uses a **greedy scheduling algorithm**:

1. Jobs are sorted by priority (C1 → C4)
2. Jobs are then sorted by call time
3. Each job is assigned to the first available ambulance
4. Ambulance availability is updated dynamically
5. Jobs that cannot be assigned are marked as unscheduled


Tech Stack

- Python
- Flask
- SQLAlchemy
- Jinja2
- HTML/CSS
- Chart.js

