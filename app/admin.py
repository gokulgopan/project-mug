from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app.models import User, Post
from app import db
from app import app


admin = Admin(app, name='Project-mug')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Post, db.session))