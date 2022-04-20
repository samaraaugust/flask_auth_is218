import logging
import flask
from flask import request, current_app, g
import os
import datetime
import time
from rfc3339 import rfc3339
from app.logs_configurations.log_formatters import RequestFormatter

log_con = flask.Blueprint('log_con', __name__)

@log_con.after_request
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
    current_app.logger.info('this is the plain message ')

    return response