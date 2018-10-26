from flask import Blueprint, request, redirect, url_for, jsonify
import json

slave_api = Blueprint('slave_api', __name__, )

@slave_api.route('/')
def root_page():
    """
    """
    return '{"json": "Slave Workin\'!"}'

@slave_api.route('/run', methods=['POST'])
def runner():
    """
    """
    data = request.data.decode()
    # data = str(request.data)
    # data = request.get_json()
    print("Data:", data, flush=True)

    # use jsonify from Flask
    # or from flask import json
    # return json.dumps({'data': json.loads(data)})
    # return jsonify({'data': json.loads(data)})
    return jsonify({'data': json.loads(data), 'status': 'Ok'})

@slave_api.route('/config') # cfg
def show_config_json():
    """
    """
    return '{"config": "Todo"}'

@slave_api.route('/version') # version {json?}
def version():
    """
    """
    return '{"version": "Perfang Todo"}'

@slave_api.route('/status') # FREE | IN WORK | ... ;; for slaves
def status():
    """
    """
    return '{"status": "Todo"}'
