from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# Global access variables
db = SQLAlchemy()
login_manager = LoginManager()


def init_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')
    app.config['EXPLAIN_TEMPLATE_LOADING'] = True
    # Initialize plugins
    db.init_app(app)
    login_manager.init_app(app)

    # here are all of the pieces of your program
    # import all python and logic files
    with app.app_context():
        from . import auth
        from .assets import compile_assets
        from .home import routes as home_routes

        db.create_all()  # create sql tables for our data models

        # register blueprints
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(home_routes.home_bp)

        # Compile static assets
        if app.config['FLASK_ENV'] == 'development':
            compile_assets(app)

        return app
