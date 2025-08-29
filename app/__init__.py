import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .config import BaseConfig


db = SQLAlchemy()


def create_app() -> Flask:
    app = Flask(__name__, template_folder=os.path.join(os.getcwd(), "templates"))
    app.config.from_object(BaseConfig)

    # Ensure instance folder exists for SQLite
    instance_path = os.path.join(os.getcwd(), "instance")
    os.makedirs(instance_path, exist_ok=True)

    db.init_app(app)

    with app.app_context():
        # Initialize DB tables
        from . import models  # noqa: F401
        db.create_all()

        from .routes import bp as main_bp
        app.register_blueprint(main_bp)

    return app

