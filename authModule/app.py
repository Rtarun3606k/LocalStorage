from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

from env import EnvConfig

db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)

log = logging.getLogger(__name__)   # ✅ THIS LINE FIXES THE ERROR

def create_app():
    app = Flask(__name__)
    app.config.from_object(EnvConfig)

    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    CORS(
        app,
        resources={r"/api/*": {"origins": EnvConfig.FRONTEND_ORIGIN}},
        supports_credentials=True
    )

    from utils.logging import setup_logging
    setup_logging()

    from utils.swagger import swagger, SWAGGER_URL
    app.register_blueprint(swagger, url_prefix=SWAGGER_URL)

    from routes.test import test_bp
    from routes.health import health_bp
    from routes.userRoutes import userRoute
    from routes.keyExchange import keyExchange_bp

    app.register_blueprint(test_bp, url_prefix="/api")
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(userRoute, url_prefix="/api/users")
    app.register_blueprint(keyExchange_bp, url_prefix="/api/keys")

    return app
