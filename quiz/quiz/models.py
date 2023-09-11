from quiz import db, login_manager
from datetime import datetime
from flask_login import UserMixin 

@login_manager.user_loader
def load_user(user_id): 
    return User.query.get(int(user_id))



class User(db.Model, UserMixin): 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),  unique=True, nullable=False) 
    pin = db.Column(db.String(12), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    classses = db.relationship('Class', backref='user', lazy=True, cascade='all, delete-orphan', passive_deletes=True)
    assignments = db.relationship('Assignment',backref='assignment', lazy=True )

   
    
    def __repr__(self): 
        return f"User('{self.username}','{self.pin}','{self.email}','{self.role}')"
    
class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),nullable=False)
    class_name = db.Column(db.String(100), nullable=False)
    class_code = db.Column(db.String(6),nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    nonuserid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # students = db.relationship('User', secondary=enrollment_table, back_populates='classes')
    assignments = db.relationship('Assignment', backref='classs', lazy=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())  # Initialized
    quizzes = db.relationship('Quiz',backref='class_',lazy=True)
    # quizzes = db.relationship('Quiz', backref='class', lazy=True)
    # assignments = db.relationship('Assignment', backref='class', lazy=True)

    def __repr__(self):
        return f"Class('{self.class_name}')"


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_attachment = db.Column(db.String(255), nullable=True)
def __repr__(self):
        return f"Assignment('{self.title}', '{self.class_id}')"
    
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    quiz_code = db.Column(db.String(5), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    timer = db.Column(db.Integer)  # Default timer in seconds
    questions = db.relationship('Question', backref='quiz', lazy=True)
    options = db.relationship('Option',backref='quiz', lazy=True)
    quizlog  = db.relationship('QuizLog',backref='quizlog', lazy=True)
    def _repr_(self):
        return f"Quiz('{self.title}')"

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    options = db.relationship('Option', backref='question', lazy=True)

    def _repr_(self):
        return f"Question('{self.text}')"
    

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    is_correct = db.Column(db.Boolean, default=False) 
    def _repr_(self):
        return f"Option('Option 1: {self.option1}', 'Option 2: {self.option2}', 'Option 3: {self.option3}', 'Option 4: {self.option4}','Is Correct: {self.is_correct}')"
        

class QuizLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entered_answer = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(200), nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f"QuizLog('Quiz ID: {self.quiz_id}', 'Student ID: {self.student_id}', 'Entered Answer: {self.entered_answer}', 'Correct Answer: {self.correct_answer}', 'Total Marks: {self.total_marks}')"


