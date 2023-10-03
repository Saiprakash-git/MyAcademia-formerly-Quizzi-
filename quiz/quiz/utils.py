import random
import string
from quiz.models import Class, Quiz, ClassStudent,User
from flask_mail import Message
from flask import url_for
from quiz import  mail

def get_people(classid):
    people = []
    classpeople = ClassStudent.query.filter_by(class_id=classid).all()
    for p in classpeople:
        data = User.query.get_or_404(p.user_id)
        people.append(data)

    return people

def assignment_added_email(user, title,msgbody):
    msg = Message(title,
                  sender='21001cs073@gmail.com',
                  recipients=[user.email])
    msg.body = msgbody
    mail.send(msg)

def classcode_generator(size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def quizcode_generator(size=5, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def live_quizcode_generator(size=5, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_users_with_assigned_quiz(class_id):
    class_ = Class.query.get(class_id)

    if class_ is None:
        return []

    # Get the users who have joined the class
    joined_users = class_.students
    users_with_assigned_quiz = []

    # Iterate through each user and check if they have been assigned any quiz in the class
    for user in joined_users:
        assigned_quizzes = Quiz.query.filter_by(class_id=class_.id).all()
        if assigned_quizzes:    
            users_with_assigned_quiz.append(user)

    return users_with_assigned_quiz


def check_class_code(classcode): 
    classs = Class.query.filter_by(class_code=classcode).first()
    return classs
