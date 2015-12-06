import os
basedir = os.path.abspath(os.path.dirname(__name__))


class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or '<Your mail username>'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '<Your mail password>'
    FLASKY_MAIL_SUBJECT_PREFIX = '[Bookmarks]'
    FLASKY_MAIL_SENDER = 'Bookmarks Admin <microblog.dummy@gmail.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') or '<Your email>'
    APPLICATION_KEY = '<your asws application key>'
    APPLICATION_SECRET = '<your aws application secret>'
    AWS_ACCESS_KEY_ID = '<your aws access id>'
    AWS_SECRET_ACCESS_KEY = '<your aws access key'>
    BUCKET_NAME = 'banesbookmarks'
    REDIS_URL = 'redis://localhost:6379/0'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
