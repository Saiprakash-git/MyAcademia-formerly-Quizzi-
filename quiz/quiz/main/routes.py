from quiz import app
from flask import  render_template, redirect, session, url_for,request
from flask_login import  current_user
from quiz.models import Class, LiveQuiz, Quiz, User
from quiz.forms import JoinQuiz
@app.route("/")
def firstpage():
    
    return render_template('firstpage.html')


@app.route("/home", methods=['GET','POST'])
def home(): 
    user = User.query.get_or_404(current_user.id)
    role = current_user.role
    form = JoinQuiz()
    if request.method == 'POST' and form.validate_on_submit():
        print("yesss")
        return redirect(url_for('join_quiz',quiz_code=form.quiz_code.data))
    if current_user.is_authenticated:
<<<<<<< HEAD:quiz/quiz/main/routes.py
        created_classes = Class.query.filter_by(creator_id=current_user.id).all()
      
        joined = ClassStudent.query.filter_by(user_id=current_user.id).all()
        joined_classes =[]
        for j in joined:
            joi = Class.query.get_or_404(j.class_id)
            joined_classes.append(joi)
             
        quizzes = LiveQuiz.query.filter_by(creator_id=current_user.id).all()
        if quizzes:
=======
        if role == 'teacher':
            classes = Class.query.filter_by(creator_id=current_user.id).all()
            
            quizzes = LiveQuiz.query.filter_by(creator_id=current_user.id).all()
           
            quizs = []
>>>>>>> parent of df5ee05 (Merge branch 'main' of https://github.com/Saiprakash-git/quiz_on_working):flask_session/quiz/quiz/main/routes.py
            for quiz in quizzes: 
                q = Quiz.query.filter_by(id=quiz.id).first()
                if q:
                    quizs.append(q)
            
<<<<<<< HEAD:quiz/quiz/main/routes.py
        return render_template('home.html', created_classes=created_classes,joined_classes=joined_classes,quizzes=quizs, user=user,form=form, username=user.username)
    
    return render_template('home.html', user=user,created_classes=created_classes,quizzes=quizs,joined_classes=joined_classes, form=form, username=user.username)
=======
        else:
            classes = user.classes_enrolled.all()
            quizzes = user.quizzes
        return render_template('home.html', classes=classes, user=user,quizzes=quizzes,form=form)
    
    return render_template('home.html', user=user,classes=classes, quizzes=quizs, form=form)
>>>>>>> parent of df5ee05 (Merge branch 'main' of https://github.com/Saiprakash-git/quiz_on_working):flask_session/quiz/quiz/main/routes.py

@app.route("/about")
def about(): 
    return render_template('about.html')
