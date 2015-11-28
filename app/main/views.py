import uuid
import boto
from flask import redirect, url_for, render_template, current_app, flash
from flask.ext.login import login_required, current_user
from . import main
from .. import db
from manage import app
from .forms import Bookmarks
from ..models import BookMarks
from GrabzIt import GrabzItClient
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import os
basedir = os.path.abspath(os.path.dirname(__file__))

with app.app_context():
    grabzIt = GrabzItClient.GrabzItClient(current_app.config['APPLICATION_KEY'],
                                          current_app.config['APPLICATION_SECRET'])
    conn = S3Connection(current_app.config['AWS_ACCESS_KEY_ID'],
                        current_app.config['AWS_SECRET_ACCESS_KEY']
                        )
    bucket_name = 'banesbookmarks'
    bucket = conn.get_bucket(bucket_name)
    k = Key(bucket)


@main.route('/')
def index():
    return redirect(url_for('auth.login'))


@main.route('/bookmarks')
@login_required
def bookmarks():
    bookmark_urls = current_user.bookmarks.all()
    return render_template('index.html', bookmarks=bookmark_urls)


def save_to_s3(url):
    grabzIt.SetImageOptions(url, width="200", height="200")
    hashvalue = uuid.uuid4()
    filepath = '%s.jpg' % str(hashvalue)
    k.key = filepath
    grabzIt.SaveTo(filepath)
    k.set_contents_from_string(open(filepath, 'r').read())
    os.remove(filepath)
    return str(hashvalue)


def save_to_local(url):
    grabzIt.SetImageOptions(url)
    hashvalue = uuid.uuid4()
    filepath = basedir + '/../static/images/%s.jpg' % str(hashvalue)
    grabzIt.SaveTo(filepath)
    return hashvalue


@main.route('/addbookmarks', methods=['GET', 'POST'])
@login_required
def add_bookmarks():
    '''
    This function adds the bookmarks to the database, and it will also check whether the url being added
    is already in users list of urls
    current_user._get_current_object() is used to get the 'current_user' object
    :return:
    '''
    form = Bookmarks()
    if form.validate_on_submit():
        url = form.bookmark_url.data
        active_user = current_user._get_current_object()
        for bookmark in active_user.bookmarks.all():
            if bookmark.url == url:
                flash('The URL u are about to add already exists')
                return redirect(url_for('main.bookmarks'))
        filename = save_to_s3(url)
        #filename = save_to_local(url)
        bookmark_object = BookMarks()
        bookmark_object.description = form.comment.data
        bookmark_object.url = url
        bookmark_object.image_url = str('https://s3-us-west-2.amazonaws.com/banesbookmarks/%s' % (filename+'.jpg'))
        bookmark_object.user = active_user
        db.session.add(bookmark_object)
        return redirect(url_for('main.bookmarks'))
    return render_template('add_bookmarks.html', form=form)