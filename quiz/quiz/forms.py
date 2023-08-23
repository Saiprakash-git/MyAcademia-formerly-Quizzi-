from flask_wtf import FlaskForm  
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms import SubmitField, StringField, PasswordField, BooleanField, SelectField, FileField, DateField, TextAreaField
from quiz.models import User, Class
from flask_login import current_user



class RegistrationForm(FlaskForm): 
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    pin = StringField('Pin',validators=[DataRequired(), Length(min=10,max=12)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('choose', 'Choose...'),('teacher', 'Teacher'), ('student', 'Student')])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
        elif  username.data.isalnum(): 
            raise ValidationError('Username should be alphanumeric (e.g., username@21001CS073)')

    def validate_pin(self, pin):
        user = User.query.filter_by(pin=pin.data).first()
        if user:
            raise ValidationError('User already exists with this PIN.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
        
        
class LoginForm(FlaskForm): 
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AddClass(FlaskForm): 
    classname = StringField('Classname', validators=[DataRequired(), Length(min=3, max=30)])
    submitfield = SubmitField('Create Class')
    
    def validate_class(self, classname):
        classobj = Class.query.filter_by(classname=classname.data).first()
        if classobj:
            raise ValidationError('Class Already Exists. create a different one')
        
class JoinClass(FlaskForm):
    classcode= StringField('classcode',validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Join Class')

class AddAssignment(FlaskForm):
    assignmenttitle = StringField('assignmenttitle', validators=[DataRequired()])
    assignmentdescription = TextAreaField('assignmentdescription',validators=[DataRequired()])
    duedate = DateField('due_date', format='%Y-%m-%d', validators=[DataRequired()])
    attachment = FileField('Attachment')
    # Add the QuerySelectField to select the class
    class_id = SelectField('Class', coerce=int)  
    
    submit = SubmitField('Add Assignment')

class UpdateAccount(FlaskForm): 
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    pin = StringField('Pin',validators=[DataRequired(), Length(min=10,max=12)])
    role = SelectField('Role', choices=[('choose', 'Choose...'),('teacher', 'Teacher'), ('student', 'Student')])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
# class Account(FlaskForm): 
    