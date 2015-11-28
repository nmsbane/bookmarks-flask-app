import hashlib
import os
import subprocess
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask.ext.login import UserMixin
from . import db, login_manager
from config import basedir
from boto.s3.connection import S3Connection
from boto.s3.key import Key


PHANTOM = '/usr/local/bin/phantomjs'
SCRIPT = os.path.join(basedir, 'screenshot.js')


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, nullable=False, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    bookmarks = db.relationship('BookMarks', backref='user', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError("password is not readable can only write")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False

        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def save_to_s3(filename):
    k.key = filename
    k.set_contents_from_string(open(filename, 'r').read())
    os.remove(filename)
    return str('https://s3-us-west-2.amazonaws.com/banesbookmarks/%s' % filename)


class BookMarks(UserMixin, db.Model):
    __tablename__ = 'bookmarks'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(256), nullable=False)
    image_url = db.Column(db.String(256), unique=True, nullable=False)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def fetch_image(self, url):
        self.url = url
        url_hash = hashlib.md5(self.url).hexdigest()
        filename = 'bookmark-%s.jpg' % url_hash
        outfile = filename
        params = [PHANTOM, SCRIPT, self.url, outfile]
        exitcode = subprocess.call(params)
        if exitcode == 0:
            self.image_url = save_to_s3(filename)
            return True
        return False

    def __repr__(self):
        return '%r' % self.url

from manage import app
with app.app_context():
    conn = S3Connection(current_app.config['AWS_ACCESS_KEY_ID'],
                        current_app.config['AWS_SECRET_ACCESS_KEY']
                        )
    bucket_name = 'banesbookmarks'
    bucket = conn.get_bucket(bucket_name)
    k = Key(bucket)