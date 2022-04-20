"""A simple flask web app"""
import flask_login
import os
import datetime
import time

from flask import g, request
from rfc3339 import rfc3339

from flask import render_template, Flask, has_request_context, request
from flask_bootstrap import Bootstrap5
from flask_wtf.csrf import CSRFProtect

from app.auth import auth
from app.auth import auth
from app.cli import create_database
from app.context_processors import utility_text_processors
from app.db import db
from app.db.models import User
from app.exceptions import http_exceptions
from app.simple_pages import simple_pages
import logging
from flask.logging import default_handler
from app.logs_configurations import log_con
login_manager = flask_login.LoginManager()

from app.logs_configurations.log_formatters import RequestFormatter

def page_not_found(e):
    return render_template("404.html"), 404

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    if app.config["ENV"] == "production":
        app.config.from_object("app.config.ProductionConfig")
    elif app.config["ENV"] == "development":
        app.config.from_object("app.config.DevelopmentConfig")
    elif app.config["ENV"] == "testing":
        app.config.from_object("app.config.TestingConfig")



    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    csrf = CSRFProtect(app)
    bootstrap = Bootstrap5(app)
    app.register_blueprint(simple_pages)
    app.register_blueprint(auth)
    app.context_processor(utility_text_processors)
    app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'Simplex'
    app.register_error_handler(404, page_not_found)
    # app.add_url_rule("/", endpoint="index")

    app.register_blueprint(log_con)
    db.init_app(app)
    # add command function to cli commands
    app.cli.add_command(create_database)

    # Deactivate the default flask logger so that log messages don't get duplicated
    app.logger.removeHandler(default_handler)

    # get root directory of project
    root = os.path.dirname(os.path.abspath(__file__))
    # set the name of the apps log folder to logs
    logdir = os.path.join(root, 'logs')
    # make a directory if it doesn't exist
    if not os.path.exists(logdir):
        os.mkdir(logdir)
    # set name of the log file
    log_file = os.path.join(logdir, 'info.log')

    handler = logging.FileHandler(log_file)
    # Create a log file formatter object to create the entry in the log
    formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )
    # set the formatter for the log entry
    handler.setFormatter(formatter)
    # Set the logging level of the file handler object so that it logs INFO and up
    handler.setLevel(logging.INFO)
    # Add the handler for the log entry
    app.logger.addHandler(handler)

    @app.before_request
    def start_timer():
        g.start = time.time()
    """
    @app.after_request
    def log_request(response):
        if request.path == '/favicon.ico':
            return response
        elif request.path.startswith('/static'):
            return response
        elif request.path.startswith('/bootstrap'):
            return response

        now = time.time()
        duration = round(now - g.start, 2)
        dt = datetime.datetime.fromtimestamp(now)
        timestamp = rfc3339(dt, utc=True)

        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        host = request.host.split(':', 1)[0]
        args = dict(request.args)

        log_params = [
            ('method', request.method),
            ('path', request.path),
            ('status', response.status_code),
            ('duration', duration),
            ('time', timestamp),
            ('ip', ip),
            ('host', host),
            ('params', args)
        ]

        request_id = request.headers.get('X-Request-ID')
        if request_id:
            log_params.append(('request_id', request_id))

        parts = []
        for name, value in log_params:
            part = name + ': ' + str(value) + ', '
            parts.append(part)
        line = " ".join(parts)
        #this triggers a log entry to be created with whatever is in the line variable
        app.logger.info('this is the plain message ')

        return response
    """
    return app


@login_manager.user_loader
def user_loader(user_id):
    try:
        return User.query.get(int(user_id))
    except:
        return None
