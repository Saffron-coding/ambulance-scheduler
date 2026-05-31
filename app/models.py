from app import db
import sqlalchemy.orm as so
import sqlalchemy as sa
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

class Job(db.Model):
    __tablename__ = 'job'
    job_id: so.Mapped[int] = so.mapped_column(db.Integer, primary_key=True)
    incident_name: so.Mapped[str] = so.mapped_column(db.String, nullable=False)
    user_assigned_category: so.Mapped[str] = so.mapped_column(sa.String(30), nullable=False)
    system_assigned_category: so.Mapped[str] = so.mapped_column(sa.String(30), nullable=False)
    call_time: so.Mapped[datetime] = so.mapped_column(db.DateTime, nullable=False)
    location: so.Mapped[str] = so.mapped_column(sa.String(30), nullable=False)
    lat: so.Mapped[float] = so.mapped_column(db.Float, nullable=False)
    lon: so.Mapped[float] = so.mapped_column(db.Float, nullable=False)
    patient_age: so.Mapped[int] = db.Column(db.Integer, nullable=False)
    patient_notes: so.Mapped[str] = so.mapped_column(sa.String(500), nullable=False)
    medical_history: so.Mapped[str]= db.Column(db.String(500), nullable=False)
    time: so.Mapped[datetime] = so.mapped_column(db.DateTime, nullable=True)


    def __repr__(self):
        return f"<Job {self.job_id}>"

class Ambulance(db.Model):
    __tablename__ = 'ambulance'
    id : so.Mapped[int] = so.mapped_column(db.Integer, primary_key=True)
    name :so.Mapped[str] = so.mapped_column(db.String, nullable=False)
    location: so.Mapped[str] = so.mapped_column(sa.String(30), nullable=False)
    lat: so.Mapped[float] = so.mapped_column(db.Float, nullable=False)
    lon: so.Mapped[float] = so.mapped_column(db.Float, nullable=False)
    available_from: so.Mapped[datetime] = so.mapped_column(db.DateTime, nullable=False)
    vehicle_type: so.Mapped[str] = so.mapped_column(db.String(50), nullable=False)
    status: so.Mapped[str] = so.mapped_column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Ambulance {self.name}>"

class Allocation(db.Model):
    __tablename__ = 'allocation'
    allocation_id : so.Mapped[int] = so.mapped_column(db.Integer, primary_key=True)
    ambulance_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("ambulance.id", ondelete="CASCADE")
                                                ,nullable=False)
    dispatch_time: so.Mapped[datetime] = so.mapped_column(db.DateTime, nullable=False)
    arrival_time: so.Mapped[datetime] = so.mapped_column(db.DateTime, nullable=False)
    clear_time: so.Mapped[datetime] = so.mapped_column(db.DateTime, nullable=False)
    response_minutes = db.Column(db.Float, nullable=False)
    service_minutes: so.Mapped[float] = so.mapped_column(db.Float, nullable=False)
    total_job_minutes: so.Mapped[float] = so.mapped_column(db.Float, nullable=False)
    outcome: so.Mapped[str] = so.mapped_column(db.String, unique=True)


