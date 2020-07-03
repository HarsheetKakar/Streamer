from flask_login import UserMixin
from streamer import db, login
from werkzeug.security import generate_password_hash, check_password_hash


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(300), nullable=False)
    watch_list = db.relationship('Watching', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Show(db.Model):
    __tablename__ = "show"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    seasons = db.relationship('Season', backref='show', lazy='dynamic')
    thumbnail = db.Column(db.String(80), default="default.jpg")

    def __init__(self, name, thumbnail):
        self.name = name
        self.thumbnail = thumbnail


class Season(db.Model):
    __tablename__ = 'season'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    videos = db.relationship('Video', backref='season', lazy='dynamic')


class Video(db.Model):
    __tablename__ = "video"
    id = db.Column(db.Integer, primary_key=True)
    season_id = db.Column(db.Integer, db.ForeignKey(
        'season.id'), nullable=False)
    path = db.Column(db.String(80), nullable=False, unique=True)
    name = db.Column(db.String(80), nullable=False)


class Watching(db.Model):
    __tablename__ = "watching"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vid_id = db.Column(db.Integer, nullable=False)
    time = db.Column(db.Integer, default=0)  # time in seconds
