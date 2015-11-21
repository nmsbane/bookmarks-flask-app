from flask import redirect, url_for, render_template
from . import main
from .forms import Bookmarks


@main.route('/')
def index():
    return redirect(url_for('auth.login'))


@main.route('/bookmarks')
def bookmarks():
    return render_template('index.html')


@main.route('/addbookmarks', methods=['GET', 'POST'])
def add_bookmarks():
    form = Bookmarks()
    return render_template('add_bookmarks.html', form=form)