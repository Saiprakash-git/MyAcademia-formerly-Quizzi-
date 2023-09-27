from quiz import app, db 
from quiz.models import Class, Assignment, User, ClassStudent
from quiz.forms import AddAssignment, AddClass, JoinClass
from quiz.utils import classcode_generator , get_user_attempted_quizzes, get_users_with_assigned_quiz
from flask_login import  current_user, logout_user, login_required
from flask import  render_template, redirect, url_for, request, flash,  request


@app.route("/addclass", methods=['GET','POST'])
@login_required
def add_class(): 
    user = User.query.filter_by(email=current_user.email).first()
    if request.method == 'POST':
        if user.role == 'teacher' : 
            form = AddClass() 
            if form.validate_on_submit(): 
                classcode = classcode_generator()
                classs = Class(username=current_user.username ,class_name=form.classname.data,class_code=classcode, creator_id=current_user.id, user_id=current_user.id)
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
    assignments = Assignment.query.filter_by(class_id=classinfo.id).all()
    userassigns = user.assignments
    quizzes = classinfo.quizzes
    quizlog = {}  # Create an empty dictionary to store quiz log entries
    
    # Iterate through the quizzes and retrieve the last attempt for each
    for quiz in quizzes:
        last_attempt = get_user_attempted_quizzes(user.id, quiz.id)
        if last_attempt:
            quizlog[quiz.id] = last_attempt
    
    participants = len(ClassStudent.query.filter_by(class_id=classid).all())
    
    #users_quizzes = get_users_with_assigned_quiz(classid)
    if classinfo:
        return render_template('classinfo.html',classinfo=classinfo, current_user=current_user,
                                assignments=assignments,userassigns=userassigns,quizzes=quizzes,quizlog=quizlog, participants=participants)


@app.route("/student/joinclass", methods=['GET','POST'])
@login_required
def join_class():
    user = User.query.filter_by(email=current_user.email).first()
    if request.method == 'POST':
        form = JoinClass()
        if form.validate_on_submit():
            class_code = request.form.get('classcode')  # Assuming you have an input field named 'class_code'
            class_to_join = Class.query.filter_by(class_code=class_code).first()
           
            if class_to_join!=None: 
                if class_to_join not in user.classes_enrolled:
                    #uid = class_to_join.creator_id
                    enrolled_classes = current_user.classes_enrolled.all()
                    enrolled_classes.append(class_to_join)
                    current_user.classes_enrolled = enrolled_classes
                    #class_to_join.user_id = uid 
                    
                    db.session.commit()
                    flash('Successfully joined the class', 'success')
                else:
                    flash('You are already enrolled in this class', 'info')
            else:
                flash('Class with the provided code not found or you do not have student access', 'danger')
            
            return redirect(url_for('home'))
        return render_template('joinclass.html',form=form)


@app.route('/class<int:class_id>/remove<int:user_id>')
def exit_class(user_id, class_id): 
    user = User.query.get(user_id)
    classs = Class.query.get(class_id)
    user.classes.remove(classs)
    db.session.commit()
    return redirect(url_for('home'))