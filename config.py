import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    JWT_SECRET_KEY = os.urandom(24)
    
    # Auth0 configuration
    AUTH0_DOMAIN = 'dev-uw7w4rwxkdv2a2x2.eu.auth0.com'
    AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET")
    AUTH0_API_AUDIENCE = os.environ.get("AUTH0_API_AUDIENCE")
    AUTH0_ALGORITHMS = ["RS256"]
