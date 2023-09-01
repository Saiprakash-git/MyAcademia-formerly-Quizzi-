from quiz import app, db , bcrypt,mail
from flask import Flask , render_template, redirect, url_for, request, flash, current_app, request, send_from_directory, send_file, session
from quiz.forms import RegistrationForm, LoginForm, AddClass , JoinClass, AddAssignment, UpdateAccount, AddQuizForm
from flask_login import login_user, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy 
from quiz.models import User, Class , Assignment, Quiz, Question, Option
import random, string 
from werkzeug.utils import secure_filename
from quiz.utils import assignment_added_email, quizcode_generator, classcode_generator, get_users_with_assigned_quiz
import os

app_ctx = app.app_context()

@app.route("/")
def firstpage():
   
     return render_template('frontpage.html')


@app.route("/home", methods=['GET'])
def home(): 
    user = current_user
    role = current_user.role
    if current_user.is_authenticated:
        if role == 'teacher':
            classes = Class.query.filter_by(user_id=current_user.id).all()
            
        else:
            classes = current_user.classses

        return render_template('home.html', classes=classes, user=user)
    
    return render_template('home.html', user=user)


@app.route("/register", methods=['GET', 'POST'])
def register(): 
    form = RegistrationForm()
    
    if form.validate_on_submit():   
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,pin=form.pin.data, email=form.email.data, role = form.role.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template("register.html",form=form)
    

@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)
    

@app.route("/logout")
def logout(): 
    logout_user()
    flash('Log Out successfull', 'info')
    return render_template('frontpage.html')

@app.route("/delete_account/<int:user_id>", methods=['GET','POST'])
def delete_account(user_id): 
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit() 
    return redirect(url_for('firstpage'))


@app.route("/about")
def about(): 
    return render_template('about.html')


def classcode_generator(size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@app.route("/addclass", methods=['GET','POST'])
@login_required
def add_class(): 
    user = User.query.filter_by(email=current_user.email).first()
    if request.method == 'POST':
        if user.role == 'teacher' : 
            form = AddClass() 
            if form.validate_on_submit(): 
                classcode = classcode_generator()
                classs = Class(username=current_user.username ,class_name=form.classname.data,class_code=classcode, user_id=current_user.id, nonuserid=current_user.id)
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
    users_quizzes = get_users_with_assigned_quiz(classid)
    if classinfo:
        return render_template('classinfo.html',classinfo=classinfo, current_user=current_user, assignments=assignments,userassigns=userassigns,quizzes=quizzes)


@app.route("/student/joinclass", methods=['GET','POST'])
@login_required
def join_class():
    user = User.query.filter_by(email=current_user.email).first()
    if request.method == 'POST':
        form = JoinClass()
        if form.validate_on_submit():
            class_code = request.form.get('classcode')  # Assuming you have an input field named 'class_code'
            class_to_join = Class.query.filter_by(class_code=class_code).first()
            uid = class_to_join.user_id 
            if class_to_join: 
                if class_to_join not in user.classses:
                    current_user.classses =current_user.classses + [class_to_join]
                    class_to_join.user_id = uid 
                    
                    
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
    user.classses.remove(classs)
    db.session.commit()
    return redirect(url_for('home'))
    


@app.route('/add_assignment', methods=['GET', 'POST'])
@login_required
def add_assignment():
    user_classes = Class.query.filter_by(user_id=current_user.id).all()
    form = AddAssignment()
    form.class_id.choices = [(class_.id, class_.class_name) for class_ in user_classes]

    if form.validate_on_submit():
        title = form.assignmenttitle.data
        description = form.assignmentdescription.data
        due_date = form.duedate.data
        class_id = form.class_id.data
        attachment = form.attachment.data  # Get the uploaded file

        if attachment:  # Check if a file was uploaded
            filename = secure_filename(attachment.filename)
            attachment_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            attachment.save(attachment_path)  # Save the file

        assignment = Assignment(title=title, description=description, due_date=due_date,
                                class_id=class_id, creator_id=current_user.id,
                                file_attachment=attachment_path)
        db.session.add(assignment)
        db.session.commit()
        #send_email(assignment)
        flash('Assignment created successfully!', 'success')
        return redirect(url_for('class_info', classid=form.class_id.data))

    return render_template('addassignment.html', form=form, user_classes=user_classes)

def send_email(assignment): 
        classid = assignment.class_id
        classs = Class.query.get(classid)
        users = User.query.all()
        title = assignment.title
        msgbody = f'Assignment Added in {classs.class_name} Due-Date:{assignment.due_date}-----------{assignment.description}'
        for user in users: 
            if classs in user.classses: 
                assignment_added_email(user,title=title, msgbody=msgbody)

@app.route('/download_attachment/<filename>', methods=['GET'])
def download_attachment(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        # Handle the case where the file does not exist
        return "File not found", 404

@app.route('/assignment/<int:assignment_id>')
def assignment_details(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    return render_template('assignmentdetails.html', assignment=assignment, current_user=current_user)

@app.route('/<int:assignment_id>/delete')
def delete_assignment(assignment_id): 
    assignment = Assignment.query.get_or_404(assignment_id)
    classid = assignment.class_id
    db.session.delete(assignment)
    db.session.commit()
    return redirect(url_for('class_info',classid=classid))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account(): 
    if current_user.role == 'teacher':
        image_file = url_for('static', filename='profiles/' + 'teacher_logo.jpg')
    if current_user.role == 'student':
        image_file = url_for('static', filename='profiles/' + 'student_logo.jpeg')
    form = UpdateAccount() 
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.pin = form.pin.data
        current_user.role = form.role.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html',current_user=current_user, image_file=image_file, form=form)



# Import necessary modules and classes
# ...


@app.route('/classinfo/Add_Quiz', methods=['GET', 'POST'])
@login_required
def add_quiz():
    user_classes = Class.query.filter_by(user_id=current_user.id).all()

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
            question_text = request.form.get(f'question_{i + 1}')  # Retrieve question text from form
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
    return render_template('quizdetails.html',quiz=quiz, current_user=current_user)

@app.route('/delete/<int:quiz_id>')
def delete_quiz(quiz_id): 
    quiz = Quiz.query.get_or_404(quiz_id)
    classid = quiz.class_id 
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    for question in questions:
        options = Option.query.filter_by(question_id=question.id).all()
        
        # Delete options for the current question
        for option in options:
            db.session.delete(option)
        
        # Delete the current question
        db.session.delete(question)
    
    # Delete the quiz
    db.session.delete(quiz)
    
    db.session.commit()
    flash('Quiz has been Deleted', 'success')
    return redirect(url_for('class_info', classid=classid))

@app.route('/quiz/attempt<int:quiz_id>')
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions  # Retrieve quiz questions
    return render_template('quiz.html', quiz=quiz, questions=questions)

@app.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
  
    questions = quiz.questions

    total_score = 0

    for question in questions:
        user_answer = request.form.get(f'question_{question.id}')
        # Compare user's answer with correct answer, update total_score

    return render_template('quizresult.html', total_score=total_score)







# Your existing models and database setup code

@app.route('/quiz/start_quiz/<int:quiz_id>')
def start_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    # Check if the quiz exists
    if quiz is None:
        return "Invalid quiz code"
    
    # Get the list of questions for the quiz
    questions = quiz.questions
    # Shuffle the questions randomly
    random.shuffle(questions)

    # Initialize the session variables for storing the current question index and the score
    if 'current_question' not in session:
        session['current_question'] = 0
    if 'score' not in session:
        session['score'] = 0
    
    # Check if the user has submitted an answer
    if request.method == 'POST':
        # Get the user's answer from the form
        answer = request.form.get('answer')
        # Get the correct answer from the database
        correct_answer = questions[session['current_question']].options[0].option1 # Assuming option1 is always correct
        # Compare the user's answer with the correct answer and update the score accordingly
        if answer == correct_answer:
            session['score'] += 1
        
        # Increment the current question index by 1
        session['current_question'] += 1
    
    # Check if there are more questions left
    if session['current_question'] < len(questions):
        # Get the current question object
        question = questions[session['current_question']]
        # Get the options for the current question
        options = question.options[0]
        # Render the quiz template with the quiz, question, and options data
        return render_template('question_template.html', quiz=quiz, question=question, options=options)
    
    else:
        # Reset the session variables
        session.pop('current_question')
        session.pop('score')
        # Render a message to indicate that the quiz is over
        return "Quiz is over. Thank you for participating."


# Push the context onto the stack
app_ctx.push()
# Perform the database operation within the application context
db.create_all()

