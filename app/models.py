from app import db

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(20), unique=True, nullable=False)
    category = db.Column(db.String(10), nullable=False)
    call_time = db.Column(db.String(30), nullable=False)
    dispatch_time = db.Column(db.String(30), nullable=False)
    arrival_time = db.Column(db.String(30), nullable=False)
    clear_time = db.Column(db.String(30), nullable=False)
    response_minutes = db.Column(db.Float, nullable=False)
    service_minutes = db.Column(db.Float, nullable=False)
    total_job_minutes = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    outcome = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Job {self.job_id}>"

class Ambulance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    available_from = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f"<Ambulance {self.name}>"

