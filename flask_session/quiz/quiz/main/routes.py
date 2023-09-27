from quiz import app
from flask import  render_template, redirect, url_for,request
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
        if role == 'teacher':
            classes = Class.query.filter_by(creator_id=current_user.id).all()
            
            quizzes = LiveQuiz.query.filter_by(creator_id=current_user.id).all()
           
            quizs = []
            for quiz in quizzes: 
                q = Quiz.query.filter_by(id=quiz.id).first()
                if q:
                    quizs.append(q)
            
        else:
            classes = user.classes_enrolled.all()
            quizzes = user.quizzes
        return render_template('home.html', classes=classes, user=user,quizzes=quizzes,form=form)
    
    return render_template('home.html', user=user,classes=classes, quizzes=quizs, form=form)

@app.route("/about")
def about(): 
    return render_template('about.html')
