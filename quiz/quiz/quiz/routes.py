import os
import PyPDF2
from docx import Document
from flask_socketio import emit, join_room
from quiz import app,db,socketio
from quiz.models import Class, PromptQuiz,Quiz,Option, Question, LiveQuiz, QuizLog, User, QuizAttempts,QuizResult
from quiz.forms import AddQuizForm, AddLiveQuizForm
from flask_login import  current_user, login_required
from quiz.utils import generate_from_file, quizcode_generator , live_quizcode_generator, generate_quiz_content, generate_quiz_title
from flask import render_template, redirect, url_for, request, flash, session ,Response
from random import shuffle
from datetime import datetime, timedelta
import re
import random


count = 0 
student_details = []
participants_in_quiz = []
current_running = []

def getParticipants(quiz_id):
    participants_in_quiz = [student for student in student_details if student['quiz_id'] == quiz_id]
    return participants_in_quiz

@app.route('/quiz/<int:class_id>', methods=['POST', 'GET'])
def add_livequiz(class_id):
    form = AddLiveQuizForm()
    quiz_code = live_quizcode_generator()

    if request.method == 'POST' and form.validate_on_submit():
        num_questions = form.num_questions.data
        quiz = Quiz(
            quiz_code=quiz_code,
            class_id=class_id,
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
                        option_letter = string.ascii_uppercase[j - 1]
                        is_correct = (option_letter == request.form.get(f'question_{i + 1}_correct_option'))
                        option = Option(
                            question_id=question.id,
                            quiz_id=quiz.id,
                            option_text=option_text,
                            option_letter=option_letter,
                            is_correct=is_correct
                        )
                        db.session.add(option)
                        db.session.commit()

        
        return render_template('startorlater.html', quiz_id=quiz.id)

    return render_template('addLivequiz.html', form=form, class_id=class_id)


@app.route('/start_live_quiz/<int:quiz_id>', methods=['GET','POST'])
def start_live_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    session['quiz_id'] = quiz.id
    # if current_user.id == livequiz.creator_id: 
    #     current_running.append(quiz_id)
    students_in_quiz  = [student for student in student_details if student['quiz_id'] == quiz_id]
    image_file = url_for('static', filename='profiles/' + 'participant.png')
    participants = len(students_in_quiz)
    return render_template('startlivequiz.html',image_file=image_file,livequiz=quiz,quiztitle=quiz.title,students_in_quiz=students_in_quiz, participants=participants, current_user=current_user)

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

#prompt generated
import re
def separate_questions_options_and_correct(content):
    lines = content.split('\n')
    questions = []
    options = []
    correct_options = []
    current_question = ""
    current_options = []  # New variable to store the options for the current question
    current_correct_option = ""
    for line in lines:
        print(f"Processing line: {line}")
        if line.strip().endswith('?'):  # Identify the line as a question if it ends with '?'
            if current_question:
                questions.append(current_question.strip())
                options.append(current_options)  # Append the options for the current question
                correct_options.append(current_correct_option.strip())
            current_question = line.strip()[:-1]  # Remove the trailing '?' to get the question
            current_options = []  # Reset the options for the new question
            current_correct_option = ""
        elif line.startswith("Answer:"):
            current_correct_option = line.split("Answer:")[1].strip()
        elif line.strip():  # If the line is not empty (ignoring empty lines)
            current_options.append(line.strip())  # Append the line to the options list for the current question

    if current_question:
        questions.append(current_question.strip())
        options.append(current_options)
        correct_options.append(current_correct_option.strip())

    return questions, options, correct_options


@app.route('/prompt', methods=['GET', 'POST'])
def prompt_page():
    if request.method == 'POST':
        prompt = request.form['prompt']
        ai_generated_content = generate_quiz_content(prompt)
        print(ai_generated_content)
        questions, options, correct_options = separate_questions_options_and_correct(ai_generated_content)
        # quiz_title = generate_quiz_title(prompt)
        quiz_title = "Title"
        print("Questions:", questions)
        print("Options:", options)
        print("Correct Options:", correct_options)
        print("Title:", quiz_title)
        return render_template('generated_quiz.html', questions=questions, options=options, correct_options=correct_options, quiz_title=quiz_title, prompt=prompt)
    return render_template('prompt_page.html')

@app.route('/save_generated_quiz', methods=['POST'])
def save_generated_quiz():
    if request.method == 'POST':
        title = request.form.get("quiz_title")
        class_id = session.get('current_classid')
        timer = request.form.get("quiz_timer")
        prompt = request.form.get("prompt")
        quiz_code = live_quizcode_generator()

        if title is not None and class_id is not None:
            quiz = Quiz(class_id=class_id, quiz_code=quiz_code, title=title, timer=timer, creator_id=current_user.id, datetime=datetime.now())
            db.session.add(quiz)
            db.session.commit()
            questions = request.form.getlist("questions[]")
            options = [request.form.getlist(f"options_{i}[]") for i in range(len(questions))]
            correct_options = request.form.getlist("correct_options[]")
            print("qs:",questions)
            print("os:",options)
            print("cos:",correct_options)
            for i, question_text in enumerate(questions):
                question = Question(quiz_id=quiz.id, text=question_text)
                db.session.add(question)
                db.session.commit()

                question_options = options[i]
                question_id = question.id

                # Use a regular expression to extract the option letter or number
                # correct_option_matches = re.finditer(r'\b([a-zA-Z]+)\)', correct_options[i])
                # correct_option_values = [match.group(1).strip() for match in correct_option_matches]
                correct_option_values = correct_options[i]
                print(f"question_text: {question_text}, correct_options[i]: {correct_options[i]}, correct_option_values: {correct_option_values}")

                for j, option_text in enumerate(question_options, start=1):
                    # Check if the option value is among the correct options
                    is_correct = option_text in correct_option_values

                    print(f"j: {j}, option_text: {option_text}, is_correct: {is_correct}")

                    option = Option(
                        question_id=question_id,
                        quiz_id=quiz.id,
                        option_text=option_text,
                        option_letter=chr(ord('A') + j - 1),
                        is_correct=is_correct
                    )
                    db.session.add(option)
                db.session.commit()
                
            quizprompt = PromptQuiz(quiz_id=quiz.id, prompt=prompt)
            db.session.add(quizprompt)

            # Consolidate commits
            db.session.commit()
            return render_template('startorlater.html', quiz_id=quiz.id)
        else:
            print("Title or class_id was NONE")

    return redirect(request.referrer)

#File quiz
def get_file_extension(file_path):
    _, file_extension = os.path.splitext(file_path)
    return file_extension

def extract_text_from_pdf(pdf_file_path):
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        text = ""
        for page in range(pdf_reader.numPages):
            text += pdf_reader.getPage(page).extractText()
    return text

def extract_text_from_docx(docx_file_path):
    doc = Document(docx_file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text
    return text

def extract_text_from_txt(txt_file_path):
    content = ''
    with open(txt_file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            content += line   
    return content

@app.route('/file_content', methods=['GET', 'POST'])
def file_content():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        instructions = request.form['instructions']
        f_content = ""
        if uploaded_file.filename != '':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(file_path)
        extension = get_file_extension(file_path)

        if extension == '.pdf':
            f_content = extract_text_from_pdf(file_path)
        elif extension == '.docx':
            f_content = extract_text_from_docx(file_path)
        elif extension == '.txt':
            f_content = extract_text_from_txt(file_path)
        else:
            flash('File type not supported','danger')
            return render_template('file_page.html')
        quiz_content = generate_from_file(f_content)
        questions, options, correct_options = separate_questions_options_and_correct(quiz_content)
        return render_template('generated_quiz.html', questions=questions, options=options, correct_options=correct_options)
    return render_template('file_page.html')


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
    quiz = Quiz.query.filter_by(quiz_code=quiz_code).first()
    user_is_creator = quiz.creator_id == current_user.id
    random.seed(current_user.id)

    if quiz is None:
        return "Invalid quiz code"
    socketio.emit('quiz_started',{'quiz_code':quiz_code})
    existing_participation = QuizResult.query.filter_by(quiz_id=quiz.id, student_id=current_user.id).first()

    if existing_participation is not None:
        flash("You have already taken this quiz.","danger")
        return redirect(url_for('quizresult', quiz_code=quiz_code))

    question = quiz.questions
    questions = list(question)
    random.shuffle(questions)
    print(questions)

    if 'current_question' not in session:
        session['current_question'] = 0

    if request.method == 'POST':   
      if user_is_creator:
        session['current_question'] += 1
      else:

         answer = request.form.get('selected_answer')
         print(answer)
         print(answer)

         correct_answer = Option.query.filter_by(
            question_id=questions[session['current_question']].id,
            is_correct=True
        ).first()

         result =0
         quizlog = QuizLog(quiz_id=quiz.id,student_id=current_user.id,entered_answer= answer, correct_answer=correct_answer.option_text,total_marks=result)
         db.session.add(quizlog)
         db.session.commit()            

         session['current_question'] += 1
        
    if session['current_question'] < len(questions):
        question = questions[session['current_question']]

        if question.options:
            num_options = Option.query.filter_by(question_id=question.id).count()
            options = Option.query.filter_by(question_id=question.id).all()
            l1 = [option.option_text for option in options]
            
            random.seed()
            random.shuffle(l1)
            print(l1)

        else:
             options = None
        if user_is_creator:
            template_name = 'teacher_questions.html'
        else:
            template_name = 'question_template.html'
    
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
    

    # Check if the quiz exists
    if quiz is None:
        return "Invalid quiz code"
    
    if quiz.creator_id == current_user.id:
        return redirect(url_for('combine_results', quiz_id =quiz.id))

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
    live_quizzes = Quiz.query.filter_by(class_id=class_id).all()

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
    total_questions = len(quiz.questions)
    return render_template('quizdetails.html',quiz=quiz, current_user=current_user, total_questions=total_questions, livequiz=quiz)

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