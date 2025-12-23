from flask import Flask

from flask_cors import CORS
# database setup
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_migrate import Migrate


# swagger setup and imports
from utils.swagger import swagger, SWAGGER_URL

# configurationsclass Config:
app = Flask(__name__)
CORS(app) 

DEBUG = True
SECRET_KEY = "your_secret_key"
JWT_SECRET = "supersecret"
JWT_REFRESH_SECRET = "refreshsecret"
PUBLIC_KEY_PATH = "keys/public_2025.pem"

# Format: postgresql://username:password@host:port/database_name
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:1234@localhost:5432/localstoragedb"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# setup logging
from utils.logging import setup_logging

setup_logging()
import logging

log = logging.getLogger(__name__)


# add limmiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    get_remote_address, app=app, default_limits=["200 per day", "50 per hour"]
)


# import blueprints
from routes.test import test_bp
from routes.health import health_bp
from routes.userRoutes import userRoute
from routes.keyExchange import keyExchange_bp


# import dtabase models
from database.test import testModel
from database.UserModel import UserModel
from database.developerModel import DeveloperModel
from database.organization import OrganizationModel
from database.services import ServicesModel
from database.userServices import UserService
from database.apiKey import ApiKey
from database.auditLog import AuditLog


# register blueprints
app.register_blueprint(test_bp, url_prefix="/api")
app.register_blueprint(health_bp, url_prefix="/api")
app.register_blueprint(swagger, url_prefix=SWAGGER_URL)
app.register_blueprint(userRoute, url_prefix="/api/users")
app.register_blueprint(keyExchange_bp, url_prefix="/api/keys")
