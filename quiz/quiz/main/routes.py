from quiz import app
from flask import  render_template, redirect, session, url_for,request
from flask_login import  current_user, login_required
from quiz.models import Class,  Quiz, User,ClassStudent

from quiz.users.routes import users



def firstpage():
    return render_template('firstpage.html')

@app.route("/home", methods=['GET','POST'])
def home():

    user = User.query.get_or_404(current_user.id)
    if request.method == 'POST' :
        quiz_code = request.form.get("quiz_code")
        return redirect(url_for('join_quiz',quiz_code=quiz_code))
    if current_user.is_authenticated:
        created_classes = Class.query.filter_by(creator_id=current_user.id).all()

        joined = ClassStudent.query.filter_by(user_id=current_user.id).all()
        joined_classes =[]
        for j in joined:
            joi = Class.query.get_or_404(j.class_id)
            joined_classes.append(joi)

        return render_template('home.html', created_classes=created_classes,joined_classes=joined_classes, user=user, username=user.username)
    
    return render_template('home.html', user=user,created_classes=created_classes,joined_classes=joined_classes,  username=user.username)

@app.route("/about")
def about(): 
    return render_template('about.html')

@app.route('/library')
@login_required
def library():
    user = User.query.filter_by(id=current_user.id).first()
    quizzes = Quiz.query.filter_by(creator_id=user.id).all()
    return render_template('library.html', quizzes=quizzes)