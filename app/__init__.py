import os
from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
csrf = CSRFProtect()
_scheduler = None


def _get_database_uri() -> str:
	configured = os.getenv("DATABASE_URL")
	if configured:
		return configured
	return "sqlite:////workspace/app.db"


def create_app() -> Flask:
	app = Flask(__name__, template_folder="../templates", static_folder="../static")

	app.config.update(
		SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret"),
		SQLALCHEMY_DATABASE_URI=_get_database_uri(),
		SQLALCHEMY_TRACK_MODIFICATIONS=False,
		SCHEDULER_API_ENABLED=False,
		PERMANENT_SESSION_LIFETIME=timedelta(days=7),
	)

	db.init_app(app)
	csrf.init_app(app)

	with app.app_context():
		from . import models  # noqa: F401
		db.create_all()

	from .routes import main_bp
	from .admin import admin_bp
	from .webhooks import webhooks_bp

	app.register_blueprint(main_bp)
	app.register_blueprint(admin_bp, url_prefix="/admin")
	app.register_blueprint(webhooks_bp, url_prefix="/webhooks")

	from .scheduler import schedule_jobs

	global _scheduler
	if _scheduler is None:
		_scheduler = BackgroundScheduler(timezone="UTC")
		schedule_jobs(_scheduler, app)
		_scheduler.start()

	return app