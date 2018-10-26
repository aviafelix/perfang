#!/usr/bin/env python3
# Служка
import argparse
from flask import Flask
from concurrent.futures import ThreadPoolExecutor
from config.default import cfg
# from xchgdata import tasks_queue, errors_queue, worker
from views.slave import slave_routes
from api.slave import slave_api

config = cfg['slave']

app = Flask(__name__)
app.config.update(
    DEBUG=config['debug'],
    TESTING=True,
    JSONIFY_PRETTYPRINT_REGULAR=False,
    TEMPLATES_AUTO_RELOAD=True,
    # SQLALCHEMY_TRACK_MODIFICATIONS=False,
    # SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.abspath(config.DB_DIR),
    # SQLALCHEMY_POOL_SIZE=1,
)

app.register_blueprint(slave_routes)
app.register_blueprint(slave_api, url_prefix='/perfang/api/slave/v0.1')
# app.register_blueprint(slave_api, url_prefix='/perfang/slave/api/v0.1')


if __name__ == '__main__':
    import os

    with open('slave-1.pid', 'w') as fpid:
        pid = os.getpid()
        fpid.write(str(pid))

    print("Main thread [{}] started".format(pid))
    app.run(**config)
