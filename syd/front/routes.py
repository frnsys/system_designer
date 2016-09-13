from flask import Blueprint, render_template

routes = Blueprint('routes', __name__)


@routes.route('/<path:filename>')
def index(filename):
    return render_template(filename)


