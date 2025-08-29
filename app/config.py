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
    XERO_REDIRECT_URI = os.getenv("XERO_REDIRECT_URI", "http://localhost:5000/xero/callback")
    XERO_SCOPES = os.getenv(
        "XERO_SCOPES",
        "offline_access accounting.transactions accounting.contacts accounting.settings openid profile email",
    )
    XERO_TENANT_ID = os.getenv("XERO_TENANT_ID", "")

    UCOLLECT_API_KEY = os.getenv("UCOLLECT_API_KEY", "")
    UCOLLECT_HOSTED_AUTH_URL = os.getenv("UCOLLECT_HOSTED_AUTH_URL", "")

    PAYADV_USERNAME = os.getenv("PAYADV_USERNAME", "")
    PAYADV_PASSWORD = os.getenv("PAYADV_PASSWORD", "")
    PAYADV_BASE_URL = os.getenv("PAYADV_BASE_URL", "https://api.payadvantage.com.au")
    PAYADV_HOSTED_URL = os.getenv("PAYADV_HOSTED_URL", "https://portal.payadvantage.com.au")

    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

