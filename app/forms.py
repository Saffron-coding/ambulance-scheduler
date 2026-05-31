from random import choices
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms import SubmitField, SelectField, DateTimeField, DecimalField, DateTimeLocalField,FloatField, TextAreaField
from wtforms.fields.numeric import IntegerField
from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField


class JobForm(FlaskForm):
    location = SelectField('Location',
                           choices =[("Harborne","Harborne"),("Quinton" ,"Quinton"),
("Bartley Green", "Bartley Green"),("Erdington", "Erdington"),("Kingstanding", "Kingstanding"),
("Castle Vale", "Castle Vale"),("Pype Hayes", "Pype Hayes"),("Moseley", "Moseley"),("Sparkhill", "Sparkhill"),
("Hall Green","Hall Green"),("Kings Heath","Kings Heath"),("Jewellery Quarter","Jewellery Quarter"),
("Newtown","Newtown"),("Northfield","Northfield"), ("Longbridge","Longbridge"),("Rubery","Rubery"),
("Rubery","Rubery"),("Rubery","Rubery"),("Handsworth Wood", "Handsworth Wood"),("Oscott","Oscott"),
("Great Barr","Great Barr"),("Selly Oak", "Selly Oak"), ("Bournville","Bournville"),("Stirchley", "Stirchley"),
("Selly Park", "Selly Park"), ("Yardley","Yardley"), ("Acocks Green","Acocks Green"),("Sheldon","Sheldon"),
("South Yardley","South Yardley"),("Four Oaks","Four Oaks"),("Roughley","Roughley"),("Walmley","Walmley"),
                                     ("Birmingham city centre","Birmingham city centre")],
                           validators=[DataRequired()])
    user_assigned_category = SelectField(
        'Category',
        choices=[('C1', 'C1'), ('C2', 'C2'), ('C3', 'C3'),('C4', 'C4')],
        validators=[DataRequired()]
    )
    call_time = DateTimeLocalField(
        'Call Time',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()]
    )

    total_job_minutes = FloatField('Duration (minutes)', validators=[DataRequired()])

    outcome = SelectField("Outcome",
                          choices=[('Hear & Treat', 'Hear & Treat'), ('Convey to ED', 'Convey to ED'),
                        ('See & Treat', 'See & Treat')],
                          validators=[DataRequired()])

    incident_name = StringField("Incident Name", validators=[DataRequired()])
    patient_notes = TextAreaField("Patient Note", validators=[DataRequired()])
    medical_history = TextAreaField("Patient Note", validators=[DataRequired()])
    patient_age = IntegerField("Patient Age", validators=[DataRequired()])


    submit = SubmitField("Add Ambulance Job")

class AmbulanceForm(FlaskForm):
    name = StringField("Ambulance Name", validators=[DataRequired()])
    location = SelectField('Location',
                           choices=[("Harborne", "Harborne"), ("Quinton", "Quinton"),
                                    ("Bartley Green", "Bartley Green"), ("Erdington", "Erdington"),
                                    ("Kingstanding", "Kingstanding"),
                                    ("Castle Vale", "Castle Vale"), ("Pype Hayes", "Pype Hayes"),
                                    ("Moseley", "Moseley"), ("Sparkhill", "Sparkhill"),
                                    ("Hall Green", "Hall Green"), ("Kings Heath", "Kings Heath"),
                                    ("Jewellery Quarter", "Jewellery Quarter"),
                                    ("Newtown", "Newtown"), ("Northfield", "Northfield"), ("Longbridge", "Longbridge"),
                                    ("Rubery", "Rubery"),
                                    ("Rubery", "Rubery"), ("Rubery", "Rubery"), ("Handsworth Wood", "Handsworth Wood"),
                                    ("Oscott", "Oscott"),
                                    ("Great Barr", "Great Barr"), ("Selly Oak", "Selly Oak"),
                                    ("Bournville", "Bournville"), ("Stirchley", "Stirchley"),
                                    ("Selly Park", "Selly Park"), ("Yardley", "Yardley"),
                                    ("Acocks Green", "Acocks Green"), ("Sheldon", "Sheldon"),
                                    ("South Yardley", "South Yardley"), ("Four Oaks", "Four Oaks"),
                                    ("Roughley", "Roughley"), ("Walmley", "Walmley"),
                                    ("Birmingham city centre", "Birmingham city centre")],
                           validators=[DataRequired()])
    available_from = DateTimeLocalField(
        "Available From",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()]
    )
    vehicle_type = StringField("Vehicle type", validators=[DataRequired()])
    submit = SubmitField("Add Ambulance")