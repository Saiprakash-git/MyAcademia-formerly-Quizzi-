from quiz import app,db 
from quiz.models import Class,Quiz,Option, Question, LiveQuiz, User
from quiz.forms import AddQuizForm, AddLiveQuizForm
from flask_login import  current_user, login_required
from quiz.utils import quizcode_generator , live_quizcode_generator
from flask import render_template, redirect, url_for, request, flash, session
from random import shuffle
from datetime import datetime

@app.route('/classinfo/Add_Quiz', methods=['GET', 'POST'])
@login_required
def add_quiz():
    user_classes = Class.query.filter_by(creator_id=current_user.id).all()

    form = AddQuizForm()
    form.class_id.choices = [(class_.id, class_.class_name) for class_ in user_classes]
    quiz_code = quizcode_generator()
    if request.method == 'POST' and form.validate_on_submit():
        num_questions = form.num_questions.data  # Get the number of questions from the form

        quiz = Quiz(
            class_id=form.class_id.data,
            quiz_code=quiz_code,
            title=form.title.data,
            timer=form.timer.data
        )
        db.session.add(quiz)
        db.session.commit()

        for i in range(num_questions):
            question_text = request.form.get(f'question_{i + 1}')  
            if question_text:
                question = Question(quiz_id=quiz.id, text=question_text)
                db.session.add(question)
                db.session.commit()

                options = []
                for j in range(1, 5):
                    option_text = request.form.get(f'question_{i + 1}_option_{j}')
                    if option_text:
                        options.append(option_text)

                if len(options) == 4:
                    option = Option(
                        question_id=question.id,
                        quiz_id=quiz.id,
                        option1=options[0],
                        option2=options[1],
                        option3=options[2],
                        option4=options[3]
                    )
                    db.session.add(option)
                    db.session.commit()

        flash('Quiz has been added', 'success')
        return redirect(url_for('class_info', classid=form.class_id.data))

    return render_template('addquiz.html', form=form, user_classes=user_classes)

@app.route('/quiz/<int:quiz_id>')
def quiz_details(quiz_id):
    quiz =Quiz.query.get_or_404(quiz_id)
    total_questions = len(quiz.questions)
    return render_template('quizdetails.html',quiz=quiz, current_user=current_user, total_questions=total_questions)

@app.route('/delete/<int:quiz_id>')
def delete_quiz(quiz_id): 
    quiz = Quiz.query.get_or_404(quiz_id)
    classid = quiz.class_id 
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    for question in questions:
        options = Option.query.filter_by(question_id=question.id).all()
        for option in options:
            db.session.delete(option)
        db.session.delete(question)
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz has been Deleted', 'success')
    return redirect(url_for('class_info', classid=classid))

@app.route('/quiz/<int:quiz_id>/submit', methods=['GET','POST'])
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions
    total_score = 0
    user_answer = []
    for question in questions:
        user_answer = request.form.get(f'question_{question.id}')
        if user_answer == 4:
            total_score+=1
    return render_template('quizresult.html', total_score=total_score)

@app.route('/start_live_quiz/<int:quiz_id>', methods=['GET','POST'])
def start_live_quiz(quiz_id):
    livequiz = LiveQuiz.query.get_or_404(quiz_id)
    quiztitle = session.get('livequiztitle')
    return render_template('startlivequiz.html',quiz_code=livequiz.quiz_code,quiztitle=quiztitle)

@app.route('/livequiz', methods=['POST','GET'])
def add_livequiz(): 
    form = AddLiveQuizForm()
    quiz_code = live_quizcode_generator()
    if request.method == 'POST' and form.validate_on_submit():
        num_questions = form.num_questions.data  # Get the number of questions from the form
        quiz = Quiz(
            quiz_code=quiz_code,
            title=form.title.data,
            timer=form.timer.data
        )
        session['livequiztitle'] = form.title.data
        db.session.add(quiz)
        db.session.commit()
        for i in range(num_questions):
            question_text = request.form.get(f'question_{i + 1}')  
            if question_text:
                question = Question(quiz_id=quiz.id, text=question_text)
                db.session.add(question)
                db.session.commit()
                options = []
                for j in range(1, 5):
                    option_text = request.form.get(f'question_{i + 1}_option_{j}')
                    if option_text:
                        options.append(option_text)
                if len(options) == 4:
                    option = Option(
                        question_id=question.id,
                        quiz_id=quiz.id,
                        option1=options[0],
                        option2=options[1],
                        option3=options[2],
                        option4=options[3]
                    )
                    db.session.add(option)
                    db.session.commit()
        livequiz = LiveQuiz(quiz_id=quiz.id, quiz_code=quiz_code,creator_id=current_user.id, datetime=datetime.now())       
        db.session.add(livequiz)
        db.session.commit()
        session['quiz_id'] = quiz.id
        flash('Quiz Created', 'success')
        return render_template('startorlater.html',quiz_id=quiz.id)
    return render_template('addLivequiz.html', form=form )

@app.route('/roughpage')
def rough():
    return ' rough page'


@app.route('/quiz/start-<int:quiz_id>')
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Quiz.questions
    print(questions)


@app.route('/JoinQuiz/<int:quiz_code>')
def join_quiz(quiz_code):
    quiz = Quiz.query.filter_by(quiz_code=quiz_code).first()
    user = User.query.filter_by(username=current_user.username).first()
    

    

@app.route('/quiz/<int:quiz_id>/results')
def quiz_result(quiz_id): 
    return ''