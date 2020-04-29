from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from elasticsearch import Elasticsearch

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
ckeditor = CKEditor(app)
app.debug = True
app.app_context()

app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']])

from app import routes, models


