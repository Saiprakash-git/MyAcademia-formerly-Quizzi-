from quiz import app, db , bcrypt
from flask import Flask , render_template, redirect, url_for, request, flash, current_app, request, send_from_directory, send_file
from quiz.forms import RegistrationForm, LoginForm, AddClass , JoinClass, AddAssignment, UpdateAccount
from flask_login import login_user, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy 
from quiz.models import User, Class , Assignment
import random, string 
from werkzeug.utils import secure_filename
import os

app_ctx = app.app_context()

@app.route("/")
def firstpage():
   
     return render_template('frontpage.html')


@app.route("/home", methods=['GET'])
def home(): 
    user = current_user
    role = current_user.role
    if current_user.is_authenticated:
        if role == 'teacher':
            classes = Class.query.filter_by(user_id=current_user.id).all()
            
        else:
            classes = current_user.classses

        return render_template('home.html', classes=classes, user=user)
    
    return render_template('home.html', user=user)


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
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)
    

@app.route("/logout")
def logout(): 
    logout_user()
    flash('Log Out successfull', 'info')
    return render_template('frontpage.html')

@app.route("/about")
def about(): 
    return render_template('about.html')


def code_generator(size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@app.route("/addclass", methods=['GET','POST'])
@login_required
def add_class(): 
    user = User.query.filter_by(email=current_user.email).first()
    if request.method == 'POST':
        if user.role == 'teacher' : 
            form = AddClass() 
            if form.validate_on_submit(): 
                classcode = code_generator()
                classs = Class(username=current_user.username ,class_name=form.classname.data,class_code=classcode, user_id=current_user.id, nonuserid=current_user.id)
                db.session.add(classs)
                db.session.commit()
                flash('Class has been created','info')
                return redirect(url_for('home'))
        else: 
            flash('Cannot create class for you account type','danger')
            return redirect(url_for("home"))
        return render_template("addclass.html",form=form)

@app.route('/_class/<int:classid>')
def class_info(classid):
    classinfo = Class.query.get_or_404(classid)
    user = User.query.filter_by(username=classinfo.username).first()
    assignments = Assignment.query.filter_by(creator_id=current_user.id).all()
    userassigns = user.assignments
    
    if classinfo:
        return render_template('classinfo.html',classinfo=classinfo, current_user=current_user, assignments=assignments,userassigns=userassigns)

@app.route('/student/classrooms')
@login_required
def student_classrooms():
    enrolled_classes = current_user.enrolled_classes
    return render_template('student/classrooms.html', enrolled_classes=enrolled_classes)

@app.route("/student/joinclass", methods=['GET','POST'])
@login_required
def join_class():
    user = User.query.filter_by(email=current_user.email).first()
    if request.method == 'POST':
        form = JoinClass()
        if form.validate_on_submit():
            class_code = request.form.get('classcode')  # Assuming you have an input field named 'class_code'
            class_to_join = Class.query.filter_by(class_code=class_code).first()
            uid = class_to_join.user_id 
            if class_to_join: 
                if class_to_join not in user.classses:
                    current_user.classses =current_user.classses + [class_to_join]
                    class_to_join.user_id = uid 
                    
                    
                    db.session.commit()
                    flash('Successfully joined the class', 'success')
                else:
                    flash('You are already enrolled in this class', 'info')
            else:
                flash('Class with the provided code not found or you do not have student access', 'danger')
            
            return redirect(url_for('home'))
        return render_template('joinclass.html',form=form)

@app.route('/add_assignment', methods=['GET', 'POST'])
@login_required
def add_assignment():
    user_classes = Class.query.filter_by(user_id=current_user.id).all()
    form = AddAssignment()
    form.class_id.choices = [(class_.id, class_.class_name) for class_ in user_classes]

    if form.validate_on_submit():
        title = form.assignmenttitle.data
        description = form.assignmentdescription.data
        due_date = form.duedate.data
        class_id = form.class_id.data
        attachment = form.attachment.data  # Get the uploaded file

        if attachment:  # Check if a file was uploaded
            filename = secure_filename(attachment.filename)
            attachment_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            attachment.save(attachment_path)  # Save the file

        assignment = Assignment(title=title, description=description, due_date=due_date,
                                class_id=class_id, creator_id=current_user.id,
                                file_attachment=attachment_path)
        db.session.add(assignment)
        db.session.commit()

        flash('Assignment created successfully!', 'success')
        return redirect(url_for('class_info', classid=form.class_id.data))

    return render_template('addassignment.html', form=form, user_classes=user_classes)

@app.route('/download_attachment/<filename>', methods=['GET'])
def download_attachment(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        # Handle the case where the file does not exist
        return "File not found", 404

@app.route('/assignment/<int:assignment_id>')
def assignment_details(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    return render_template('assignmentdetails.html', assignment=assignment, current_user=current_user)

@app.route('/<int:assignment_id>/delete')
def delete_assignment(assignment_id): 
    assignment = Assignment.query.get_or_404(assignment_id)
    classid = assignment.class_id
    db.session.delete(assignment)
    db.session.commit()
    return redirect(url_for('class_info',classid=classid))
@app.route('/account')
@login_required
def account(): 
    return render_template('account.html',current_user=current_user)

@app.route('/account/update_account')
@login_required
def update_account(): 
    form = update_account() 
    

    return 


# Push the context onto the stack
app_ctx.push()

# Perform the database operation within the application context
db.create_all()

