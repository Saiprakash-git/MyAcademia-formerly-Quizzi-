import random
import string
from quiz.models import Class, Quiz, ClassStudent,User
from flask_mail import Message
from flask import url_for
from quiz import  mail
import openai 
import os 




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

def live_quizcode_generator(size=5, chars=string.digits):
    chars = chars.replace('0', '')  
    return ''.join(random.choice(chars) for _ in range(size))



openai.api_key = os.environ.get('OPENAI_API_KEY') 

def generate_quiz_content(prompt):
    inst = "Generate the required content  format : Question : Question?\n a)option1\n b)option2\n c)option3\n d)option4 "
    inst += "and after each question options print the correct answer as format:'Answer: letter) value'"
    inst += "Note:Don't Generate anything out of quiz content and use only lower-case alphabets for listing purposes And Write the Quiz title in the first line(just print only title)"
    prompt_to_ai = prompt + inst
    parameters = {
        'model': 'gpt-3.5-turbo',
        'messages': [{'role': 'system', 'content': 'You are a helpful assistant.'}, 
                     {'role': 'user', 'content': prompt_to_ai}]
    }
    response = openai.ChatCompletion.create(**parameters)
    quiz_content = response.choices[0].message.content
 
    return quiz_content

def generate_from_file(query):
    inst = "On this Paragraph of content Generate the required content  format : Question : Question?\n a)option1\n b)option2\n c)option3\n d)option4 "
    inst += "and after each question options print the correct answer as format:'Answer: letter) value'"
    inst += "Note:Don't Generate anything out of quiz content and use only lower-case alphabets for listing purposes And Write the Quiz title in the first line(just print only title)"
    prompt = "/'"+query+"/'" + inst 
    parameters = {
        'model': 'gpt-3.5-turbo',
        'messages': [{'role': 'system', 'content': 'You are a helpful assistant.'}, 
                     {'role': 'user', 'content': prompt}]
    }
    response = openai.ChatCompletion.create(**parameters)
    chat_reply = response.choices[0].message.content
    
    return chat_reply
