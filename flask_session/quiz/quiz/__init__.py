from flask import Flask, current_app
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import os

app = Flask(__name__)
with app.app_context():
    app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    UPLOAD_FOL = os.path.join(app.root_path, 'static', 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOL

db = SQLAlchemy(app)
bcrypt = Bcrypt()
login_manager = LoginManager(app) 
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
socketio = SocketIO(app)

app.config['MAIL_SERVER'] = 'smtp.googlemail.com' 
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')

mail = Mail(app)

from quiz.users import routes
from quiz.main import routes
from quiz.Class import routes 
from quiz.quiz import routes 
from quiz.assignment import routes

    
app_ctx = app.app_context()

app_ctx.push()
db.create_all()

