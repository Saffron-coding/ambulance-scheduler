from app import db
import sqlalchemy.orm as so
import sqlalchemy as sa
from datetime import datetime

class Job(db.Model):
    __tablename__ = 'job'
    id: so.Mapped[int] = so.mapped_column(db.Integer, primary_key=True)
    episode_id: so.Mapped[int] = so.mapped_column(db.Integer, nullable=False, index=True)
    incident_name: so.Mapped[str] = so.mapped_column(db.String, nullable=False)
    user_assigned_category: so.Mapped[str] = so.mapped_column(sa.String(30), nullable=False)
    call_time: so.Mapped[datetime] = so.mapped_column(db.DateTime, nullable=False)
    estimated_job_time: so.Mapped[float] = so.mapped_column(db.Float, nullable=False)
    location: so.Mapped[str] = so.mapped_column(sa.String(30), nullable=False)
    lat: so.Mapped[float] = so.mapped_column(db.Float, nullable=False)
    lon: so.Mapped[float] = so.mapped_column(db.Float, nullable=False)
    patient_age: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    medical_history: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    patient_notes: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)



    def __repr__(self):
        return f"<Job {self.id}>"

class Ambulance(db.Model):
    __tablename__ = 'ambulance'
    id : so.Mapped[int] = so.mapped_column(db.Integer, primary_key=False)
    name :so.Mapped[str] = so.mapped_column(db.String, nullable=True)
    location: so.Mapped[str] = so.mapped_column(sa.String(30), nullable=False)
    lat: so.Mapped[float] = so.mapped_column(db.Float, nullable=False)
    lon: so.Mapped[float] = so.mapped_column(db.Float, nullable=False)
    available_from: so.Mapped[datetime] = so.mapped_column(db.DateTime, nullable=False)
    vehicle_type: so.Mapped[str] = so.mapped_column(db.String(50), nullable=False)
    equipment_type: so.Mapped[str] = so.mapped_column(db.String(50), nullable=False)


    def __repr__(self):
        return f"<Ambulance {self.name}>"

class Allocation(db.Model):
    __tablename__ = 'allocation'
    id : so.Mapped[int] = so.mapped_column(db.Integer, primary_key=False)
    ambulance_id: so.Mapped[int] = so.mapped_column(db.ForeignKey("ambulance.id", ondelete="CASCADE")
                                                ,nullable=False, index=False)
    job_id: so.Mapped[int] = so.mapped_column(db.ForeignKey("job.id", ondelete="CASCADE"),
                                              nullable=False, index=False)
    arrival_time: so.Mapped[datetime] = so.mapped_column(db.DateTime, nullable=False)
    clear_time: so.Mapped[datetime] = so.mapped_column(db.DateTime, nullable=False)
    response_minutes: so.Mapped[float] = so.mapped_column(db.Float, nullable=False)
    total_job_minutes: so.Mapped[float] = so.mapped_column(db.Float, nullable=False)
    outcome: so.Mapped[str] = so.mapped_column(db.String, nullable=False)


