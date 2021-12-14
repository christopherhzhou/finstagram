from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager
from . import config
from .utils import current_time
import base64


@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()


class User(db.Document, UserMixin):
    uid = db.StringField(required=True, unique=True)
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    profile_pic = db.ImageField()

    following = db.ListField(db.StringField())

    # Returns unique string identifying our object
    def get_id(self):
        return self.username


class Post(db.Document):
    poster = db.ReferenceField(User, required=True)
    image = db.ImageField()
    caption = db.StringField(required=True, min_length=1, max_length=500)
    date = db.StringField(required=True)

    # list of users that liked it
    likers = db.ListField(db.ReferenceField(User))


class Comment(db.Document):
    post = db.ReferenceField(Post, required=True)
    commenter = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=1, max_length=500)
    date = db.StringField(required=True)
