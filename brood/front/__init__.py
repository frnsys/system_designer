import os
from flask import Flask
from .routes import routes

static_folder = os.path.join(os.getcwd(), 'static')
template_folder = os.path.join(os.getcwd(), 'templates')


def front_app(package_name=__name__, blueprints=[], static_folder=static_folder, template_folder=template_folder, **config_overrides):
    print(template_folder)
    app = Flask(package_name,
                static_url_path='/static',
                static_folder=static_folder,
                template_folder=template_folder)

    # apply overrides
    app.config.update(config_overrides)

    blueprints.append(routes)
    # register blueprints
    for bp in blueprints:
        app.register_blueprint(bp)

    return app
