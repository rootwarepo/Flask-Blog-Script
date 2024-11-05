from flask import Flask
from models import db
import locale
from dotenv import load_dotenv
import os

# .env dosyasını yükler
load_dotenv()

locale.setlocale(locale.LC_TIME, 'tr_TR.UTF-8')

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
POSTS_PER_PAGE = 5

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS') == 'True'

db.init_app(app)
