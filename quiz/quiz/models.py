from quiz import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
class ClassStudent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(7), nullable=False)
    classes_enrolled = db.relationship('Class', backref='students', lazy='dynamic', cascade="all, delete-orphan")
    quizzes = db.relationship('Quiz', backref='user', lazy=True, cascade="all, delete-orphan")
    
    assignments = db.relationship('Assignment', backref='user', lazy=True, cascade="all, delete-orphan")


class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False) 
    class_name = db.Column(db.String(100), nullable=False)
    class_code = db.Column(db.String(6), nullable=False, unique=True)
    creator_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assignments = db.relationship('Assignment', backref='class', lazy=True, cascade="all, delete-orphan")
    quizzes = db.relationship('Quiz', backref='class', lazy=True, cascade="all, delete-orphan")

    def _repr_(self):
        return f"Class('id: {self.id}')"

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_attachment = db.Column(db.String(255), nullable=True)
    assignment_scores = db.relationship('Assignment_Score', cascade='all, delete-orphan')
    
class Assignment_Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id') , nullable=False)
    student_username = db.Column(db.Integer, db.ForeignKey('user.username'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    uploaded_assignment  = db.Column(db.String(255), nullable=True)
    points = db.Column(db.Integer, nullable=False)
    points_scored = db.Column(db.Integer)
   
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    quiz_code = db.Column(db.String(5), nullable=False, unique=True)
    title = db.Column(db.String(100), nullable=False)
    timer = db.Column(db.Integer)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    prompt_uploaded = db.relationship('PromptQuiz', backref='quiz', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    # Relationship with Option
    options = db.relationship('Option', backref='question', lazy=True)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    option_text = db.Column(db.String(200), nullable=False)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)

class PromptQuiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    prompt = db.Column(db.String(500), nullable=True)

class FileQuiz(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'),nullable=False)
    file_attachment = db.Column(db.String(255), nullable=True)



class LiveQuiz(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    quiz_code = db.Column(db.String(5), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    def __repr__(self):
            return f"LiveQuiz('quiz_id:{self.quiz_id}','quiz_code:{self.quiz_code}')"


class QuizLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entered_answer = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(200), nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f"QuizLog('Quiz ID: {self.quiz_id}', 'Student ID: {self.student_id}', 'Entered Answer: {self.entered_answer}', 'Correct Answer: {self.correct_answer}', 'Total Marks: {self.total_marks}')"
    
class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)
    quiz = db.relationship('Quiz', backref='results')


    def __repr__(self):
        return f"QuizResult('Quiz ID: {self.quiz_id}', 'Student ID: {self.student_id}', 'Total Marks: {self.total_marks}')"
