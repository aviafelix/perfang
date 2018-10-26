from flask import Blueprint, request, redirect, url_for
import json
from xchgdata import tasks_queue, errors_queue

master_api = Blueprint('master_api', __name__, )

@master_api.route('/')
def root_page():
    """
    """
    return '{"json": "Master Workin\'!"}'

@master_api.route('/run', methods=['POST'])
def runner():
    """
    """
    tasks_queue.put(json.loads(request.data.decode()))
    return json.dumps({'status': 'Ok'})

@master_api.route('/errors_queue')
def status_queue():
    """
    """
    r = []
    while not errors_queue.empty():
        r.append(str(errors_queue.get()))

    return '{{"json": "{message}"}}'.format(message='<br />\\n'.join(r))

@master_api.route('/config') # cfg
def show_config_json():
    """
    """
    return '{"config": "Todo"}'

@master_api.route('/version') # version {json?}
def version():
    """
    """
    return '{"version": "Perfang Todo"}'

@master_api.route('/status') # FREE | IN WORK | ... ;; for slaves
def status():
    """
    """
    return '{"status": "Todo"}'
