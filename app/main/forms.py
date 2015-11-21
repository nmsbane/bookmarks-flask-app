from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Required, URL, Length


class Bookmarks(Form):
    bookmark_url = StringField('Bookmark URL', validators=[Required(), Length(1, 256), URL()])
    comment = TextAreaField('About the URL', validators=[Required(), Length(1, 64)])
    submit = SubmitField('Add Bookmark')
