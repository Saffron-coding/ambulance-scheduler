from __future__ import annotations
from datetime import timedelta, datetime
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app import db
from app.models import Job, Ambulance
from app.forms import JobForm, AmbulanceForm
from app.scheduler import run_scheduler

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

    if form.validate_on_submit():
        job = Job(
            job_id=str(uuid.uuid4()),  # quick unique id
            location=form.location.data,
            category=form.category.data,
            call_time=str(form.call_time.data),
            dispatch_time="",
            arrival_time="",
            clear_time="",
            response_minutes=0.0,
            service_minutes=0.0,
            total_job_minutes=form.total_job_minutes.data,
            outcome=form.outcome.data
        )

        db.session.add(job)
        db.session.commit()

        flash('You have successfully added an ambulance job')
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
        job.total_job_minutes = form.total_job_minutes.data
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
        ambulance = Ambulance(
            name=form.name.data,
            location=form.location.data,
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
    print(ambulances)

    scheduled_jobs, unscheduled_jobs = run_scheduler(jobs, ambulances)

    return render_template(
        'schedule.html',
        scheduled_jobs=scheduled_jobs,
        unscheduled_jobs=unscheduled_jobs
        )