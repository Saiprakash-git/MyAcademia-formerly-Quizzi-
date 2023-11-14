from flask_socketio import emit, join_room
from quiz import app,db,socketio
from quiz.models import Class,Quiz,Option, Question, LiveQuiz, QuizLog, User, QuizAttempts,QuizResult
from quiz.forms import AddQuizForm, AddLiveQuizForm
from flask_login import  current_user, login_required
from quiz.utils import quizcode_generator , live_quizcode_generator, generate_quiz_content, generate_quiz_title
from flask import render_template, redirect, url_for, request, flash, session ,Response
from random import shuffle
from datetime import datetime, timedelta
import re



count = 0 
student_details = []
participants_in_quiz = []
current_running = []

def getParticipants(quiz_id):
    participants_in_quiz = [student for student in student_details if student['quiz_id'] == quiz_id]
    return participants_in_quiz

@app.route('/quiz/<int:class_id>', methods=['POST','GET'])
def add_livequiz(class_id): 
    form = AddLiveQuizForm()
    quiz_code = live_quizcode_generator()
    if request.method == 'POST' and form.validate_on_submit():
        num_questions = form.num_questions.data
        quiz = Quiz(
        quiz_code=quiz_code,
        class_id= class_id,
        title=form.title.data,
        timer=form.timer.data)
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
        return render_template('startorlater.html',quiz_id=quiz.id)
    return render_template('addLivequiz.html', form=form, class_id=class_id )


import re

def separate_questions_and_options(content):
    lines = content.split('\n')
    questions = []
    options = []
    current_question = ""
    for line in lines:
        if re.match(r'^\d+\.', line):
            if current_question:
                questions.append(current_question)
            current_question = line
            options.append([])  # Start a new list for options
        else:
            if current_question:
                options[-1].append(line)

    # Append the last question and its options
    if current_question:
        questions.append(current_question)

    return questions, options


@app.route('/prompt', methods=['GET', 'POST'])
def prompt_page():
    if request.method == 'POST':
        prompt = request.form['prompt']
        ai_generated_content = generate_quiz_content(prompt)
        questions, options = separate_questions_and_options(ai_generated_content)
        quiz_title = generate_quiz_title(prompt)
        print("Qlsssss:",questions)
        print("optons:",options)
        print("title:",quiz_title)
        return render_template('generated_quiz.html',questions=questions,options=options, quiz_title=quiz_title)
    return render_template('prompt_page.html')



@app.route('/save_generated_quiz', methods=['POST'])
def save_generated_quiz():
    if request.method == 'POST':
        title = request.form.get("quiz_title")
        questions = request.form.getlist("questions[]")
        options = request.form.getlist("options[]")
        class_id = session.get('current_classid')
        quiz_code = live_quizcode_generator()
        if questions is not None and options is not None:
            quiz = Quiz(class_id=class_id, quiz_code=quiz_code, title=title, timer=15)
            db.session.add(quiz)
            db.session.commit()

            for i, question_text in enumerate(questions):
                question = Question(quiz_id=quiz.id, text=question_text)
                db.session.add(question)
                db.session.commit()

                options_for_question = options[i].split(",")  # Split options string into a list
                option = Option(
                    question_id=question.id,
                    quiz_id=quiz.id,
                    option1=options_for_question[0],
                    option2=options_for_question[1],
                    option3=options_for_question[2],
                    option4=options_for_question[3]
                )
                
                db.session.add(option)
                livequiz = LiveQuiz(quiz_id=quiz.id, quiz_code=quiz_code,creator_id=current_user.id, datetime=datetime.now())       
                db.session.add(livequiz)
                db.session.commit()
            
            return render_template('startorlater.html', quiz_id=quiz.id)
        else:
            print("IT was NONEEEEEE")

    return redirect(request.referrer)


@app.route('/generate_quiz', methods=['GET','POST'])
def generate_quiz():
    if request.method == 'POST':
        prompt = request.form.get('prompt')
        ai_generated_content = generate_quiz_content(prompt)
        questions, options = separate_questions_and_options(ai_generated_content)
        
    return f"{ai_generated_content}"

@app.route('/start_live_quiz/<int:quiz_id>', methods=['GET','POST'])
def start_live_quiz(quiz_id):
    livequiz = LiveQuiz.query.filter_by(quiz_id=quiz_id).first()
    quiz = Quiz.query.get_or_404(quiz_id)
    session['quiz_id'] = quiz.id
    # if current_user.id == livequiz.creator_id: 
    #     current_running.append(quiz_id)
    students_in_quiz  = [student for student in student_details if student['quiz_id'] == quiz_id]
    image_file = url_for('static', filename='profiles/' + 'participant.png')
    participants = len(students_in_quiz)
    return render_template('startlivequiz.html',image_file=image_file,livequiz=livequiz,quiztitle=quiz.title,students_in_quiz=students_in_quiz, participants=participants, current_user=current_user)

@app.route('/join_quiz/<int:quiz_code>', methods=['POST', 'GET'])
def join_quiz(quiz_code):
    username = session['current_user']['username']
    quiz = Quiz.query.filter_by(quiz_code=quiz_code).first()
    if quiz!= None :
        session['current_quiz'] = {
            'quiz_id': quiz.id,
            'quiz_code': quiz.quiz_code,
            'title': quiz.title,
            'timer': quiz.timer
        }
        global student_details
        student_details.append({'quiz_id': quiz.id, 'username': username})
        return redirect(url_for('start_live_quiz', quiz_id=quiz.id))
    else:
        flash("No Quiz Found",'danger')
        return redirect(url_for('home'))
    

@socketio.on('user_join')
def handle_join():
    quiz_id = session.get('quiz_id')
    print("Quiz ID from session:", quiz_id)  
    global student_details
    for student in student_details:
        print("Student:", student)
    print("Cunt value: ",count)
    participants = len([student for student in student_details if student['quiz_id'] == quiz_id])
    print("Participants:", participants)  
    socketio.emit('quiz_joined', {"username": current_user.username, "participant_count": participants})

@app.route('/exit_quiz')
def exit_quiz():
    student_details.clear()
    current_running.clear()
    
    return redirect(url_for('home'))


# @app.route('/running_quiz/<int:quiz_code>', methods=['GET','POST'])
# def running_quiz(quiz_code):
#     quiz = Quiz.query.filter_by(quiz_code=quiz_code).first()
#     if quiz is None:
#         return "Invalid quiz code"
#     socketio.emit('quiz_started',{'quiz_code':quiz_code})
#     question = quiz.questions
#     import random
#     questions = list(question)
#     random.shuffle(questions)
#     # Initialize the session variables for storing the current question index and the score
#     if 'current_question' not in session:
#         session['current_question'] = 0
#     if 'score' not in session:
#         session['score'] = 0
    
#     # Check if the user has submitted an answer
#     if request.method == 'POST':
#         print("fromm consollllleeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
#         # Get the user's answer from the form
#         answer = request.form.get('answer')
#         # Get the correct answer from the database
#         correct_answer = questions[session['current_question']].options[0].option4 # Assuming option1 is always correct
#         # Compare the user's answer with the correct answer and update the score accordingly
#         if answer == correct_answer:
#             session['score'] += 1
#         # Increment the current question index by 1	
#         session['current_question'] += 1
#     # Check if there are more questions left
#     if session['current_question'] < len(questions):
#         # Get the current question object
#         question = questions[session['current_question']]
#         # Get the options for the current question
#         if question.options:
#             options = question.options[0]
#         else:
#              options = None
        
#         # Render the quiz template with the quiz, question, and options data
#         return render_template('question_template.html', quiz=quiz, question=question, options=options, timer=quiz.timer)
    
#     else:
#         result = session['score']
#         # Reset the session variables
#         session.pop('current_question')
#         session.pop('score')
#         # Render a message to indicate that the quiz is over
#         # quizlog = QuizLog(quiz_id=quiz.id,student_id=current_user.id,entered_answer=answer, correct_answer=correct_answer, total_marks=result)
#         # db.session.add(quizlog)
#         # db.session.commit()
#         return render_template("quizresult.html",result=result)
@app.route('/running_quiz/<int:quiz_code>', methods=['GET','POST'])
def running_quiz(quiz_code):
    # quiz = Quiz.query.get(quiz_code)
    quiz = Quiz.query.filter_by(quiz_code=quiz_code).first()
    live_quiz = LiveQuiz.query.filter_by(quiz_id=quiz.id).first()
    user_is_creator = live_quiz.creator_id == current_user.id
# Set the seed with the user's ID
    import random

    random.seed(current_user.id)

# Check if the quiz exists
    if quiz is None:
         return "Invalid quiz code"
    socketio.emit('quiz_started',{'quiz_code':quiz_code})

    existing_participation = QuizResult.query.filter_by(quiz_id=quiz.id, student_id=current_user.id).first()

    # if existing_participation is not None:
    #     flash("You have already taken this quiz.","danger")
    #     return redirect(url_for('quizresult', quiz_code=quiz_code))


    
    question = quiz.questions
    questions = list(question)

# Shuffle the questions
    random.shuffle(questions)

    print(questions)

    import random
    # Convert questions to a list
    # Initialize the session variables for storing the current question index and the score
    if 'current_question' not in session:
        session['current_question'] = 0
    # Shuffle the questions randomly and select a subset

    
 # Initialize 'answer' with a default value
 # Check if the user has submitted an answer
    if request.method == 'POST':   
      if user_is_creator:
        session['current_question'] += 1
      else:

         answer = request.form.get('selected_answer')
         print(answer)
         print(answer)

        #  answer_data = request.get_json()
        #  entered_answer = answer_data.get('answer')

        # Get the correct answer from the database
         correct_answer = questions[session['current_question']].options[0].option4 # Assuming option1 is always correct
         result =0
         quizlog = QuizLog(quiz_id=quiz.id,student_id=current_user.id,entered_answer= answer, correct_answer=correct_answer,total_marks=result)
         db.session.add(quizlog)
         db.session.commit()            
        # Increment the current question index by 1	
         session['current_question'] += 1
        # Check if there are more questions left
    if session['current_question'] < len(questions):
        # Get the current question object
        question = questions[session['current_question']]
        # Get the options for the current question
        if question.options:
            options = question.options[0]
            l1=[options.option1, options.option2,options.option3,options.option4]
            print(l1)
            random.seed()
            random.shuffle(l1)
            print(l1)

        else:
             options = None
    # Determine the template to render based on whether the user is the creator
        if user_is_creator:
            template_name = 'teacher_questions.html'
        else:
            template_name = 'question_template.html'
    
        # Render the quiz template with the quiz, question, and options data
        return render_template( template_name, quiz=quiz, question=question, l1=l1, timer=quiz.timer)
    

        # if user_is_creator:
        # # Render the quiz template with the quiz, question, and options data
        #     return render_template( 'teacher_questions.html', quiz=quiz, question=question, l1=l1, timer=quiz.timer)
        # else:
        #     return render_template( 'question_template.html', quiz=quiz, question=question, l1=l1, timer=quiz.timer)


    else:
        print(session.pop('current_question'))

        return redirect(url_for('quizresult', quiz_code=quiz_code))
        


@app.route('/quizresult/<int:quiz_code>')
@login_required  # Ensure the user is logged in
def quizresult(quiz_code):
    # Retrieve the quiz object
    quiz = Quiz.query.filter_by(quiz_code=quiz_code).first()
    live_quiz = LiveQuiz.query.filter_by(quiz_id=quiz.id).first()

    # Check if the quiz exists
    if quiz is None:
        return "Invalid quiz code"
    
    if live_quiz.creator_id == current_user.id:
        return redirect(url_for('combine_results', quiz_id =live_quiz.quiz_id))

    # Calculate the total marks for the current student
    student_id = current_user.id  # Assuming you have a way to get the current user's ID
    

    quiz_logs = QuizLog.query.filter_by(quiz_id=quiz.id, student_id=student_id).all()
    
    total_marks = 0

   # Initialize total_marks outside the loop
    for quiz_log in quiz_logs:

        if quiz_log.entered_answer == quiz_log.correct_answer:
            total_marks += 1  # Increment total_marks when the condition is met

    print(total_marks)   # Initialize total_marks outside the loop
 # This will print the total number of correct answers

    
    # Create a new entry in the results table
    quiz_result = QuizResult(quiz_id=quiz.id, student_id=student_id, total_marks=total_marks)
    db.session.add(quiz_result)
    db.session.commit()

    # You can also query and display the results for the current student
    student_results = QuizResult.query.filter_by(student_id=student_id).all()

    return render_template('quizresult.html', result=quiz_result, total_marks=total_marks, student_results=student_results)

@app.route('/combine_results/<int:quiz_id>')
def combine_results(quiz_id):
    # Retrieve quiz results for the specified quiz
    results = QuizResult.query.filter_by(quiz_id=quiz_id).all()
    quiz = Quiz.query.get_or_404(quiz_id)
    total_questions = len(quiz.questions)

    # Create a dictionary to store results grouped by student
    student_results = {}

    for result in results:
        student_id = result.student_id
        total_marks = result.total_marks

        # Get the student's username
        user = User.query.get(student_id)
        student_name = user.username

        # If the student is not in the dictionary, create an entry
        if student_name not in student_results:
            student_results[student_name] = {
                'total_marks': total_marks,
                'results': []
            }

        # Append the result for the student
        student_results[student_name]['results'].append(total_marks)

    return render_template('combine_results.html', student_results=student_results, max_marks=total_questions)

@app.route('/teacher_dashboard/<int:class_id>')
@login_required
def teacher_dashboard(class_id):
    # ... your existing code to fetch live quizzes and quiz results ...
    current_class = Class.query.get_or_404(class_id)
    if current_user.id != current_class.creator_id:
        flash('You do not have access to this class.', 'danger')
        return redirect(url_for('main.home'))

    # Get all live quizzes for the specified class
    live_quizzes = LiveQuiz.query.filter_by(class_id=class_id).all()

    # Create a dictionary to store average quiz scores for each student
    student_avg_scores = {}

    # Fetch all the quizzes associated with the class
    quizzes = Quiz.query.filter_by(class_id=class_id).all()

    # Determine the number of quizzes for which you want to calculate the average
    num_quizzes_to_use = len(quizzes)


    for quiz in quizzes:
        quiz_id = quiz.id
        quiz_results = QuizResult.query.filter_by(quiz_id=quiz_id)

        for result in quiz_results:
            student = result.student_id

            # Retrieve the student's name based on the ID
            student_name = User.query.get(student).username

            total_marks = result.total_marks

            if student_name not in student_avg_scores:
                student_avg_scores[student_name] = {
                    'total_marks': total_marks,
                    'num_quizzes': 1,
                    'quiz_marks': {quiz_id: total_marks}
                }
            else:
                student_avg_scores[student_name]['total_marks'] += total_marks
                student_avg_scores[student_name]['num_quizzes'] += 1
                student_avg_scores[student_name]['quiz_marks'][quiz_id] = total_marks

    # Calculate the average score for each student using the specified number of quizzes
    for student, data in student_avg_scores.items():
        total_marks = data['total_marks']
        num_quizzes = num_quizzes_to_use  # Use the constant number of quizzes
        average_score = round(total_marks / num_quizzes, 2)
        student_avg_scores[student]['average_score'] = average_score

    return render_template('teacher_dashboard.html', live_quizzes=live_quizzes, student_avg_scores=student_avg_scores, quizzes=quizzes)



@app.route('/student_results/<int:class_id>')
@login_required
def student_results(class_id):
    # Get the class based on the provided class_id
    current_class = Class.query.get_or_404(class_id)
    
    # Check if the current user is a member of this class
    
    # Fetch all quizzes associated with the class
    quizzes = Quiz.query.filter_by(class_id=class_id).all()
    
    # Create a dictionary to store the student's results for each quiz
    student_quiz_results = {}
    
    # Loop through the quizzes and fetch the results for the current user
    for quiz in quizzes:
        quiz_id = quiz.id
        
        # Fetch the quiz results for the current user and quiz
        quiz_result = QuizResult.query.filter_by(quiz_id=quiz_id, student_id=current_user.id).first()
        
        if quiz_result:
            # If results are found, add them to the dictionary
            student_quiz_results[quiz.title] = quiz_result.total_marks
    
    return render_template('student_results.html', student_quiz_results=student_quiz_results)

@app.route('/quiz_details/<int:quiz_id>')
def quiz_details(quiz_id):
    quiz =Quiz.query.get_or_404(quiz_id)
    livequiz = LiveQuiz.query.filter_by(quiz_id=quiz_id).first()
    total_questions = len(quiz.questions)
    return render_template('quizdetails.html',quiz=quiz, current_user=current_user, total_questions=total_questions, livequiz=livequiz)

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


@app.route('/quiz/<int:quiz_id>/results')
def quiz_result(quiz_id): 
    return ''


# Function to parse AI-generated quiz content into questions and options
def parse_ai_generated_quiz(quiz_content):
    questions_and_options = re.split(r'[A-D]\.', quiz_content)  # Split on A., B., C., D.
    
    questions = []
    options = []

    for segment in questions_and_options:
        segment = segment.strip()
        if segment:
            if segment[0].isalpha():  
                options.append(segment)
            else:   
                questions.append(segment)
    print("question:",questions)
    print("options:",options)
    return questions, options, questions_and_options