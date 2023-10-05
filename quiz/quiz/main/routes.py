from quiz import app
from flask import  render_template, redirect, session, url_for,request
from flask_login import  current_user
from quiz.models import Class, LiveQuiz, Quiz, User,ClassStudent
from quiz.forms import JoinQuiz
@app.route("/")
def firstpage():
    return render_template('firstpage.html')

@app.route("/home", methods=['GET','POST'])
def home(): 
    user = User.query.get_or_404(current_user.id)
    form = JoinQuiz()
    quizs = []
    if request.method == 'POST' and form.validate_on_submit():
        return redirect(url_for('join_quiz',quiz_code=form.quiz_code.data))
    if current_user.is_authenticated:
        created_classes = Class.query.filter_by(creator_id=current_user.id).all()
      
        joined = ClassStudent.query.filter_by(user_id=current_user.id).all()
        joined_classes =[]
        for j in joined:
            joi = Class.query.get_or_404(j.class_id)
            joined_classes.append(joi)
             
        quizzes = LiveQuiz.query.filter_by(creator_id=current_user.id).all()
        if quizzes:
            for quiz in quizzes: 
                q = Quiz.query.filter_by(id=quiz.id).first()
                if q:
                    quizs.append(q)
        else:
            quizzes = user.quizzes
            
        return render_template('home.html', created_classes=created_classes,joined_classes=joined_classes,quizzes=quizs, user=user,form=form, username=user.username)
    
    return render_template('home.html', user=user,created_classes=created_classes,quizzes=quizs,joined_classes=joined_classes, form=form, username=user.username)

@app.route("/about")
def about(): 
    return render_template('about.html')
