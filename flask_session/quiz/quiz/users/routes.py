from quiz import app,db, bcrypt
from quiz.models import User
from quiz.forms import RegistrationForm,LoginForm , UpdateAccount
from flask import  render_template, redirect, session, url_for, request, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import or_

@app.route("/register", methods=['GET', 'POST'])
def register(): 
    form = RegistrationForm()   
    
    if form.validate_on_submit():   
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,pin=form.pin.data, email=form.email.data, role = form.role.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template("register.html",form=form)
    

@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            or_(User.username == form.username.data, User.pin == form.username.data)
        ).first()

        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            session['current_user'] = { 
                'id':user.id,
                'username':user.username, 
                'pin':user.pin,
                'email':user.email,
                'role':user.role
            }
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)
    

@app.route("/logout")
def logout(): 
    logout_user()
    flash('Log Out successfull', 'info')
    return redirect(url_for('login'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account(): 
    if current_user.role == 'teacher':
        image_file = url_for('static', filename='profiles/' + 'teacher_logo.jpg')
    if current_user.role == 'student':
        image_file = url_for('static', filename='profiles/' + 'student_b.jpg')
    form = UpdateAccount() 
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.pin = form.pin.data
        current_user.role = form.role.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html',current_user=current_user, image_file=image_file, form=form)

@app.route("/delete_account/<int:user_id>", methods=['GET','POST'])
def delete_account(user_id): 
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit() 
    return redirect(url_for('firstpage'))
