import uuid
from flask import redirect, url_for, render_template, current_app, flash
from flask.ext.login import login_required, current_user
from . import main
from .. import db
from manage import app
from .forms import Bookmarks
from ..models import BookMarks
from GrabzIt import GrabzItClient
import os
basedir = os.path.abspath(os.path.dirname(__file__))

with app.app_context():
    grabzIt = GrabzItClient.GrabzItClient(current_app.config['APPLICATION_KEY'],
                                          current_app.config['APPLICATION_SECRET'])


@main.route('/')
def index():
    return redirect(url_for('auth.login'))


@main.route('/bookmarks')
@login_required
def bookmarks():
    bookmark_urls = current_user.bookmarks.all()
    return render_template('index.html', bookmarks=bookmark_urls)


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
        for bookmark in current_user._get_current_object().bookmarks.all():
            if bookmark.url == url:
                flash('The URL u are about to add already exists')
                return redirect(url_for('main.bookmarks'))
        filename = save_to_local(url)
        bookmark_object = BookMarks()
        bookmark_object.description = form.comment.data
        bookmark_object.url = url
        bookmark_object.image_url = str(filename)
        bookmark_object.user = current_user._get_current_object()
        db.session.add(bookmark_object)
        flash("please wait while we are adding the bookmark")
        return redirect(url_for('main.bookmarks'))
    return render_template('add_bookmarks.html', form=form)