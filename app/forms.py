from random import choices

from wtforms.validators import DataRequired, Length, NumberRange
from wtforms import SubmitField, SelectField, DateTimeField, DecimalField, DateTimeLocalField,FloatField
from wtforms.fields.numeric import IntegerField
from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField


class JobForm(FlaskForm):
    location = StringField('Location', validators=[DataRequired()])
    category = SelectField(
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

    submit = SubmitField("Add Ambulance Job")

class AmbulanceForm(FlaskForm):
    name = StringField("Ambulance Name", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    available_from = DateTimeLocalField(
        "Available From",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()]
    )
    submit = SubmitField("Add Ambulance")