from flask_mail import Message
from flask import url_for
from quiz import  mail


def assignment_added_email(user, title,msgbody):
    msg = Message(title,
                  sender='21001cs073@gmail.com',
                  recipients=[user.email])
    msg.body = msgbody
    mail.send(msg)