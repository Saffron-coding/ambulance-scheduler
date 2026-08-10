from __future__ import annotations
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Job, Ambulance
from app.forms import JobForm, AmbulanceForm
from scheduling.greedy_based_scheduler import run_scheduler
from app.Utils import locations

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('index.html')

@main_bp.route('/jobs')
def jobs():
    all_jobs = Job.query.all()
    return render_template('jobs.html', jobs=all_jobs)

@main_bp.route('/jobs/add', methods=['GET', 'POST'])
def add_job():
    form = JobForm()
#review with supervisor if users should reduce fields to form
    if form.validate_on_submit():
        location_name = form.location.data
        lat, lng = locations[location_name]

        job = Job(
            incident_name = form.incident_name.data,
            location=form.location.data,
            latitude = lat,
            longitude = lng,
            user_assigned_category=form.category.data,
            call_time=form.call_time.data,
            estimated_job_time= form.estimated_job_time,
            medical_history= form.medical_history.data,
            patient_notes= form.patient_notes.data,
            patient_age= form.patient_age.data

        )

        db.session.add(job)
        db.session.commit()

        flash('You have successfully triaged an ambulance job')
        return redirect(url_for('main.jobs'))

    return render_template('create_job.html', form=form)


@main_bp.route('/jobs/edit/<int:id>', methods=['GET', 'POST'])
def edit_job(id):
    job = Job.query.get_or_404(id)
    if request.method == 'GET' and job.call_time:
        job.call_time = datetime.strptime(job.call_time, "%Y-%m-%d %H:%M")
    form = JobForm(obj=job)
    if form.validate_on_submit():
        job.location = form.location.data
        job.category = form.category.data
        job.call_time = form.call_time.data.strftime("%Y-%m-%d %H:%M")
        job.estimated_job_time = form.estimated_job_time.data
        job.outcome = form.outcome.data
        db.session.commit()
        flash('You have updated the job')
        return redirect(url_for('main.jobs'))

    return render_template('edit_job.html', form=form)

@main_bp.route('/jobs/delete/<int:id>', methods=['POST'])
def delete_job(id):
    job = Job.query.get_or_404(id)
    db.session.delete(job)
    db.session.commit()
    flash('You have deleted this ambulance job')
    return redirect(url_for('main.jobs'))

@main_bp.route('/ambulances')
def ambulances():
    ambulances = Ambulance.query.all()
    return render_template('ambulances.html', ambulances=ambulances)

@main_bp.route('/ambulances/add', methods=['GET', 'POST'])
def add_ambulance():
    form = AmbulanceForm()
    if form.validate_on_submit():
        location_name = form.location.data
        lat, lng = locations[location_name]

        ambulance = Ambulance(
            name=form.name.data,
            location=form.location.data,
            latitude=lat,
            longitude=lng,
            vehicle_type=form.vehicle_type,
            equipment_type=form.equipment_type,
            available_from=form.available_from.data.strftime("%Y-%m-%d %H:%M")
        )
        db.session.add(ambulance)
        db.session.commit()
        flash('Ambulance added successfully')
        return redirect(url_for('main.ambulances'))
    return render_template('ambulance.html', form=form)

@main_bp.route('/schedule')
def schedule():
	jobs = Job.query.all()
	ambulances = Ambulance.query.all()

	scheduled_jobs, unscheduled_jobs = run_scheduler(jobs, ambulances)


	print(f"Scheduled: {len(scheduled_jobs)}")
	print(f"Unscheduled: {len(unscheduled_jobs)}")

	return render_template(
		'schedule.html',
		scheduled_jobs=scheduled_jobs,
		unscheduled_jobs=unscheduled_jobs
	)
