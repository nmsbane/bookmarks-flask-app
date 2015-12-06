from flask import redirect, url_for, render_template, flash
from flask.ext.login import login_required, current_user
from . import main
from app import db
from .forms import Bookmarks
from ..models import BookMarks
import os
basedir = os.path.abspath(os.path.dirname(__file__))


@main.route('/')
def index():
    return redirect(url_for('auth.login'))


@main.route('/bookmarks')
@login_required
def bookmarks():
    bookmark_urls = current_user.bookmarks.all()
    return render_template('index.html', bookmarks=bookmark_urls)


@main.route('/addbookmarks', methods=['GET', 'POST'])
@login_required
def add_bookmarks():
    from extensions import fetch_image
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
        bookmark_object = BookMarks()
        bookmark_object.description = form.comment.data
        bookmark_object.url = url
        bookmark_object.user = active_user
        fetch_image.delay(bookmark_object, url, active_user)
        flash('Your added bookmark is being processed and uploaded')
        db.session.commit()
        return redirect(url_for('main.bookmarks'))
    return render_template('add_bookmarks.html', form=form)