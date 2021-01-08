from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, SelectMultipleField, PasswordField
from wtforms.validators import DataRequired

date = [('1', '2020-03-01'), ('2', '2020-03-02'), ('3', '2020-03-03'), ('4', '2020-03-04'),
        ('5', '2020-03-05'), ('6', '2020-03-06'), ('7', '2020-03-07'), ('8', '2020-03-08'),
        ('9', '2020-03-09'), ('10', '2020-03-10'), ('11', '2020-03-11'), ('12', '2020-03-12'),
        ('13', '2020-03-13'), ('14', '2020-03-14'), ('15', '2020-03-15'), ('16', '2020-03-16'),
        ('17', '2020-03-17'), ('18', '2020-03-18'), ('19', '2020-03-19'), ('20', '2020-03-20'),
        ('21', '2020-03-21'), ('22', '2020-03-22'), ('23', '2020-03-23'), ('24', '2020-03-24'),
        ('25', '2020-03-25'), ('26', '2020-03-26'), ('27', '2020-03-27'), ('28', '2020-03-28'),
        ('29', '2020-03-29'), ('30', '2020-03-30'), ('31', '2020-03-31')]

time = [('0', '00:00'), ('1', '01:00'), ('2', '02:00'), ('3', '03:00'), ('4', '04:00'), ('5', '05:00'),
        ('6', '06:00'), ('7', '07:00'), ('8', '08:00'), ('9', '09:00'), ('10', '10:00'), ('11', '11:00'),
        ('12', '12:00'), ('13', '13:00'), ('14', '14:00'), ('15', '15:00'), ('16', '16:00'),
        ('17', '17:00'), ('18', '18:00'), ('19', '19:00'), ('20', '20:00'), ('21', '21:00'),
        ('22', '22:00'), ('23', '23:00')]


class LogInForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    login = SubmitField('Log in')


class SelectComDateForm(FlaskForm):
    company = SelectMultipleField('Company', choices=[('Lyft', 'Lyft'), ('Spin', 'Spin')], validators=[DataRequired()])
    startDate = SelectField('Start Date', choices=date, validate_choice=False)
    endDate = SelectField('End Date', choices=date, validate_choice=False)
    search = SubmitField('search')


class SelectComTimeForm(FlaskForm):
    company = SelectMultipleField('Company', choices=[('Lyft', 'Lyft'), ('Spin', 'Spin')], validators=[DataRequired()])
    startTime = SelectField('Start Time', choices=time, validate_choice=False)
    endTime = SelectField('End Time', choices=time, validate_choice=False)
    search = SubmitField('search')


class SelectZoneDateForm(FlaskForm):
    zone = SelectMultipleField('No Parking Zone', choices=[('Monument', 'Monument'), ('SportStadium', 'SportStadium'),
                                                           ('Georgetown', 'Georgetown')], validators=[DataRequired()])
    startDate = SelectField('Start Date', choices=date, validate_choice=False)
    endDate = SelectField('End Date', choices=date, validate_choice=False)
    search = SubmitField('search')


class SelectWardTimeForm(FlaskForm):
    ward = SelectMultipleField('Ward', choices=[('1', '1'), ('2', '2'),
                                                ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
                                                ('8', '8')], validators=[DataRequired()])
    startTime = SelectField('Start Time', choices=time, validate_choice=False)
    endTime = SelectField('End Time', choices=time, validate_choice=False)
    search = SubmitField('search')


class SelectWardDateForm(FlaskForm):
    ward = SelectMultipleField('Ward', choices=[('1', '1'), ('2', '2'),
                                                ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
                                                ('8', '8')], validators=[DataRequired()])
    startDate = SelectField('Start Date', choices=date, validate_choice=False)
    endDate = SelectField('End Date', choices=date, validate_choice=False)
    search = SubmitField('search')
