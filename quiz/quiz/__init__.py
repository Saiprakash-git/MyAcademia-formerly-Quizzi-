from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
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

from quiz import routes