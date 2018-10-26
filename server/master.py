#!/usr/bin/env python3
# Мастер
import argparse
from flask import Flask
from concurrent.futures import ThreadPoolExecutor
from config.default import cfg
from xchgdata import tasks_queue, errors_queue, worker
from views.master import master_routes
from api.master import master_api

config = cfg['master']

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

app.register_blueprint(master_routes)
app.register_blueprint(master_api, url_prefix='/perfang/api/master/v0.1')
# app.register_blueprint(master_api, url_prefix='/perfang/master/api/v0.1')


if __name__ == '__main__':
    import os

    with open('master-0.pid', 'w') as fpid:
        pid = os.getpid()
        fpid.write(str(pid))

    print("Main thread [{}] started".format(pid))
    with ThreadPoolExecutor(2) as executor:
        executor.submit(worker, cfg, tasks_queue)
        app.run(**config)
