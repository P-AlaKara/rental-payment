import os
from dotenv import load_dotenv


load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(os.getcwd(), 'instance', 'app.db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # External integrations
    XERO_CLIENT_ID = os.getenv("XERO_CLIENT_ID", "")
    XERO_CLIENT_SECRET = os.getenv("XERO_CLIENT_SECRET", "")
    XERO_TENANT_ID = os.getenv("XERO_TENANT_ID", "")

    UCOLLECT_API_KEY = os.getenv("UCOLLECT_API_KEY", "")

    PAYADV_API_KEY = os.getenv("PAYADV_API_KEY", "")
    PAYADV_PUBLIC_KEY = os.getenv("PAYADV_PUBLIC_KEY", "")
    PAYADV_WEBHOOK_SECRET = os.getenv("PAYADV_WEBHOOK_SECRET", "")

    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

