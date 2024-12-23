from quiz import app, db 
from quiz.models import Class, Assignment, User, ClassStudent
from quiz.forms import AddAssignment, AddClass, JoinClass
from quiz.utils import classcode_generator, get_people
from flask_login import  current_user, logout_user, login_required
from flask import  render_template, redirect, session, url_for, request, flash,  request

@app.route("/addclass", methods=['GET','POST'])
@login_required
def add_class(): 
    if request.method == 'POST':
        if current_user.role == 'teacher':
            try:
                form = AddClass() 
                if form.validate_on_submit(): 
                    classcode = classcode_generator()
                    check = Class.query.filter_by(class_code=classcode).first() 
                    if check: 
                        classcode= classcode_generator()
                    classs = Class(username=current_user.username ,class_name=form.classname.data,class_code=classcode, creator_id=current_user.id, user_id=current_user.id)
                    db.session.add(classs)
                    db.session.commit()
                    flash('Class has been created','info')
                    return redirect(url_for('home'))
            except Exception:
                flash("An Error Occured, Try Again",'danger')
        else: 
            flash("Class Can't be Created : As a Student ","info")
            return redirect(url_for('home'))
            
    return render_template('addclass.html',form=form)
        
@app.route('/_class/<int:classid>')
def class_info(classid):
    classinfo = Class.query.get_or_404(classid)
    session['current_classid'] = classinfo.id
    user = User.query.filter_by(username=classinfo.username).first()
    assignments = Assignment.query.filter_by(class_id=classinfo.id).all()
    userassigns = user.assignments
    quizzes = classinfo.quizzes
    participants = len(ClassStudent.query.filter_by(class_id=classid).all())
    session['participants'] = participants
   
    people = get_people(classid)
   
    if classinfo:
        return render_template('classinfo.html',classinfo=classinfo, current_user=current_user,
                                assignments=assignments,userassigns=userassigns,quizzes=quizzes, participants=participants,  people=people)


@app.route("/joinclass", methods=['GET','POST'])
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
                    joined = ClassStudent(user_id=current_user.id, class_id=class_to_join.id)
                    #class_to_join.user_id = uid 
                    db.session.add(joined)
                    db.session.commit()
                    flash('Successfully joined the class', 'success')
                else:
                    flash('You are already enrolled in this class', 'info')
            else:
                flash('Class with the provided code not found ', 'danger')
            
            return redirect(url_for('home'))
        return render_template('joinclass.html',form=form)


@app.route('/class<int:class_id>/remove<int:user_id>')
def exit_class(user_id, class_id): 
   
    classstu_instance = ClassStudent.query.filter_by(user_id=user_id,class_id=class_id).first()
    db.session.delete(classstu_instance)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/delete_class/<int:class_id>')
@login_required
def delete_class(class_id):
    class_to_delete = Class.query.get(class_id)
    if class_to_delete and current_user.id == class_to_delete.creator_id:
        ClassStudent.query.filter_by(class_id=class_id).delete()
        db.session.delete(class_to_delete)
        db.session.commit()

        flash('Class and associated data have been successfully deleted.', 'success')
    else:
        flash('You do not have permission to delete this class.', 'danger')

    return redirect(url_for('home'))