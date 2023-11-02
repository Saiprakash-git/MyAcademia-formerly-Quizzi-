from quiz import app,db, bcrypt, socketio , sse
from quiz.models import User
from quiz.forms import RegistrationForm,LoginForm , UpdateAccount
from flask import  render_template, redirect, session, url_for, request, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import or_

users = []

def generate_session_id():
    import uuid
    return str(uuid.uuid4())

@app.route("/register", methods=['GET', 'POST'])
def register(): 
    form = RegistrationForm()
    if form.validate_on_submit():   
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template("register.html",form=form)


@app.route("/", methods=['GET','POST'])
@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            or_(User.username == form.username.data)
        ).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            session['current_user'] = { 
                'id':user.id,
                'username':user.username, 
                'email':user.email,
                
            }
            users.append(user.username)
            # sse.publish({"message": f"{user.username} joined the quiz"}, type='new_user')
           
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful', 'danger')
    return render_template('login.html', title='Login', form=form)
    

@app.route("/logout")
def logout(): 
    logout_user()
    flash('Log Out successfull', 'info')
    session.clear()
    return redirect(url_for('login'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account(): 
    
    image_file = url_for('static', filename='profiles/' + 'teacher_logo.jpg')
    form = UpdateAccount() 
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
    
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        print("IM hereeeeeeeeeee")
    return render_template('account.html',current_user=current_user, image_file=image_file, form=form)

@app.route("/delete_account/<int:user_id>", methods=['GET','POST'])
def delete_account(user_id): 
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit() 
    return redirect(url_for('register'))
