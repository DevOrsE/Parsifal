from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .routes import main_bp
    from .auth import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app