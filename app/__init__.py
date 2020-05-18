from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
import uuid
from app.config import Config
# Init
db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
migrate = Migrate()
def create_app(config_class=Config):
    # init
    app = Flask(__name__)
    app.config.from_object(Config)
    #current schema
    from app import models
    # dependancies
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    mail.init_app(app)
    # routes
    from app.users.routes import users
    from app.main.routes import main
    app.register_blueprint(users)
    app.register_blueprint(main)
    return app
