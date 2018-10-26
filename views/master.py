from flask import Blueprint, request, redirect, url_for

master_routes = Blueprint('master_routes', __name__, )

@master_routes.route('/')
def root_page():
    """
    """

    return 'Master Workin\'!'

@master_routes.route('/version') # version {json?}
def version():
    """
    """
    return 'Todo'

@master_routes.route('/status') # FREE | IN WORK | ... ;; for slaves
def status():
    """
    """
    return 'Todo'
