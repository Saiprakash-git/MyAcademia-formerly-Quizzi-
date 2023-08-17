from quiz import app, db , bcrypt
from flask import Flask , render_template, redirect, url_for, request, session, flash
from quiz.forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user
from flask_sqlalchemy import SQLAlchemy 
from quiz.models import User

app_ctx = app.app_context()

@app.route("/")
@app.route("/home", methods=['GET'])
def home(): 
    return render_template('home.html')


@app.route("/register", methods=['GET', 'POST'])
def register(): 
    form = RegistrationForm()
    
    if form.validate_on_submit(): 
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, role = form.role.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template("register.html",form=form)
    

@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)
    

@app.route("/about")
def about(): 
    return render_template('about.html')





# Push the context onto the stack
app_ctx.push()

# Perform the database operation within the application context
db.create_all()

