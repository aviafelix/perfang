from flask import Blueprint, request, redirect, url_for

slave_routes = Blueprint('slave_routes', __name__, )

@slave_routes.route('/')
def root_page():
    """
    """
    return 'Slave Workin\'!'

@slave_routes.route('/version') # version {json?}
def version():
    """
    """
    return 'Todo'

@slave_routes.route('/status') # FREE | IN WORK | ... ;; for slaves
def status():
    """
    """
    return 'Todo'
