import subprocess
import uuid
import os
from config import basedir
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from config import Config
from flask import render_template
from manage import celery

PHANTOM = '/usr/local/bin/phantomjs'
SCRIPT = os.path.join(basedir, 'screenshot.js')


def save_to_s3(filename):
    k.key = filename
    k.set_contents_from_string(open(filename, 'r').read())
    os.remove(filename)
    return str('https://s3-us-west-2.amazonaws.com/banesbookmarks/%s' % filename)


@celery.task
def fetch_image(self, url, active_user):
    self.url = url
    url_hash = uuid.uuid4()
    filename = 'bookmark-%s.jpg' % url_hash
    outfile = filename
    params = ['node', SCRIPT, url, outfile]
    exitcode = subprocess.call(params)
    if exitcode == 0:
        self.user = active_user
        self.image_url = save_to_s3(filename)
        from app import db
        db.session.add(self)
        db.session.commit()
        return True
    return render_template('error.html')


conn = S3Connection(Config.AWS_ACCESS_KEY_ID,
                    Config.AWS_SECRET_ACCESS_KEY
                    )
bucket_name = 'banesbookmarks'
bucket = conn.get_bucket(bucket_name)
k = Key(bucket)
