from quiz import app,db,socketio 
from quiz.models import Class,Quiz,Option, Question, LiveQuiz, QuizLog, User, QuizAttempts, QuizResult
from quiz.forms import AddQuizForm, AddLiveQuizForm
from flask_login import  current_user, login_required
from quiz.utils import quizcode_generator , live_quizcode_generator
from flask import render_template, redirect, url_for, request, flash, session
from datetime import datetime, timedelta


student_details = []
participant_list = []
current_running = []




@app.route('/livequiz/<int:class_id>', methods=['POST','GET'])
def add_livequiz(class_id): 

    form = AddLiveQuizForm()
    quiz_code = live_quizcode_generator()
    print("=======",class_id)
    user_classes = Class.query.filter_by(creator_id=current_user.id).all()
    if request.method == 'POST' and form.validate_on_submit():
        num_questions = form.num_questions.data  
        
        if class_id:
            
            quiz = Quiz(
                quiz_code=quiz_code,
                class_id= class_id,
                title=form.title.data,
                timer=form.timer.data
            )
        else:
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
        
        return render_template('startorlater.html',quiz_id=quiz.id)
    return render_template('addLivequiz.html', form=form,user_classes=user_classes, class_id=class_id )

@app.route('/start_live_quiz/<int:quiz_id>', methods=['GET','POST'])
def start_live_quiz(quiz_id):
    livequiz = LiveQuiz.query.get_or_404(quiz_id)
    quiz = Quiz.query.get_or_404(quiz_id)
    if current_user.id == livequiz.creator_id: 
        current_running.append(quiz)
    students_in_quiz = [student for student in student_details if student['quiz_id'] == quiz_id]
    image_file = url_for('static', filename='profiles/' + 'participant.png')
    participants = len(students_in_quiz)
    
    return render_template('startlivequiz.html',image_file=image_file,livequiz=livequiz,quiztitle=quiz.title,students_in_quiz=students_in_quiz, participants=participants, current_user=current_user)

@app.route('/JoinQuiz/<int:quiz_code>', methods=['POST','GET'])
def join_quiz(quiz_code):
    username = session['current_user']['username']
    quiz = Quiz.query.filter_by(quiz_code=quiz_code).first()
    print(quiz)
    if quiz:
        socketio.emit('participant_joined', {'username': username})
        session['current_quiz'] = {
            'quiz_id':quiz.id,
            'quiz_code':quiz.quiz_code, 
            'title':quiz.title,
            'timer':quiz.timer
        } 
    student_details.append({'quiz_id': quiz.id, 'username':username})
    return redirect(url_for('start_live_quiz',quiz_id=quiz.id))

# @app.route('/JoinQuiz', methods=['POST', 'GET'])
# def join_quiz():
#     username = request.form.get('username')
#     quiz_code = request.form.get('quiz_code')
#     print("==============",quiz_code,"username",username)
  
#     quiz = Quiz.query.filter_by(quiz_code=quiz_code).first()
#     print(quiz)
#     if quiz :
#         socketio.emit('participant_joined', {'username': username})
#         print('emmittinggg')
        
#         # participant_list.append({'quiz_id': quiz.id, 'username':username})
#         attempts = QuizAttempts(quiz_id=quiz.id,student_id=session['current_user']['id'],quiz_code=quiz_code)
#         db.session.add(attempts)
#         db.session.commit() 
        
#         return redirect(url_for('start_live_quiz',quiz_id=quiz.id))
#     else: 
#         flash("No Quiz Found","info")
#         return redirect(url_for('home'))

# @socketio.on('join_quiz')
# def handle_join_quiz(data):
#     username = data['username']
#     quiz_id = data['quiz_id']

#     # Store student details
#     student_details.append({'quiz_id': quiz_id, 'username': username})

#     # Emit an event to notify all clients about the new student joining
#     emit('join_quiz', {'username': username, 'quiz_id': quiz_id}, broadcast=True)


@app.route('/exit_quiz')
def exit_quiz(): 
    student_details.clear()
    
    return redirect(url_for('home'))

@app.route('/quiz/start-<int:quiz_id>')
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Quiz.questions
    print(questions)

# @app.route('/running_quiz/<int:quiz_code>', methods=['GET','POST'])
# def running_quiz(quiz_code):
#     # quiz = Quiz.query.get(quiz_code)
#     quiz = Quiz.query.filter_by(quiz_code=quiz_code).first()

#     # Check if the quiz exists
#     if quiz is None:
#         return "Invalid quiz code"
#     question = quiz.questions
#     import random

#     # Convert questions to a list
#     questions = list(question)
    

#     # Shuffle the questions randomly and select a subset
#     # random.shuffle(questions)
#     print(questions)


#     # Initialize the session variables for storing the current question index and the score
#     if 'current_question' not in session:
#         session['current_question'] = 0
#     if 'score' not in session:
#         session['score'] = 0
    
#     # Check if the user has submitted an answer
#     if request.method == 'POST':
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
#         quizlog = QuizLog(quiz_id=quiz.id,student_id=current_user.id,entered_answer=answer, correct_answer=correct_answer, total_marks=result)
#         db.session.add(quizlog)
#         db.session.commit()
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
    existing_participation = QuizResult.query.filter_by(quiz_id=quiz.id, student_id=current_user.id).first()

    if existing_participation is not None:
        flash("You have already taken this quiz.","danger")
        return redirect(url_for('quizresult', quiz_code=quiz_code))


    
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
    

    else:
        print(session.pop('current_question'))

        return redirect(url_for('quizresult', quiz_code=quiz_code))


@app.route('/quizresult/<int:quiz_code>')
@login_required  # Ensure the user is logged in
def quizresult(quiz_code):
    # Retrieve the quiz object
    quiz = Quiz.query.filter_by(quiz_code=quiz_code).first()

    # Check if the quiz exists
    if quiz is None:
        return "Invalid quiz code"

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


@app.route('/teacher_quiz/<int:quiz_code>', methods=['GET', 'POST'])
def teacher_quiz(quiz_code):
    quiz = Quiz.query.filter_by(quiz_code=quiz_code).first()
    # Check if the quiz exists
    if quiz is None:
        return "Invalid quiz code"
    
    # Retrieve the questions from the quiz
    questions = quiz.questions

    # Check if it's the first visit to the page
    if 'shuffled_questions' not in session and 'current_question' not in session:
    # Shuffling logic here
        # Convert questions to a list and shuffle them randomly
        shuffled_questions = list(questions)
        import random
        random.shuffle(shuffled_questions)
        print(shuffled_questions)

        session['shuffled_questions'] = shuffled_questions
        session['current_question'] = 0

    shuffled_questions = session['shuffled_questions']
    
    # Check if a user has submitted an answer
    if request.method == 'POST':
        # Increment the current question index by 1
        session['current_question'] += 1

    # Check if there are more questions left
    if session['current_question'] < len(shuffled_questions):
        # Get the current question object
        current_question = shuffled_questions[session['current_question']]
        
        # Get the options for the current question
        if current_question.options:
            options = current_question.options[0]
        else:
            options = None

        # Render the quiz template with the quiz, current question, and options data
        return render_template('teacher_questions.html', quiz=quiz, question=current_question, options=options, timer=quiz.timer)
    else:
        # Reset the session variables for the next quiz attempt
        session.pop('shuffled_questions')
        session.pop('current_question')

        return render_template("quizresult.html")




@socketio.on('quiz_started')
def start_quiz(data):
    quiz_url = data['quizUrl']
 
    socketio.emit('redirect_to_quiz', quiz_url, room=request.sid)



# @app.route('/quiz_result/<int:quiz_id>/<int:score>')
# def quiz_result(quiz_id, score):
#     quiz = Quiz.query.get_or_404(quiz_id)
#     return render_template('quizresult.html', quiz=quiz, score=score)
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


@app.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    score = 0
    for question in quiz.questions:
        selected_option_id = int(request.form.get(f'question_{question.id}'))
        selected_option = Option.query.get(selected_option_id)
        if selected_option.is_correct:
            score += 1

    # Save the score in the database or take any other necessary actions

    return redirect(url_for('quiz_result', quiz_id=quiz.id, score=score))
