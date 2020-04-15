from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager 
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from app.config import Config
# Init
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    # init
    app = Flask(__name__)
    app.config.from_object(Config)
    # dependancies
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    # routes
    from app.users.routes import users
    from app.main.routes import main
    from app.departments.routes import departments
    from app.requesttypes.routes import requesttypes
    from app.serverapprovals.routes import serverapprovals
    from app.serverrequestgroups.routes import serverrequestgroups
    from app.serverrights.routes import serverrights
    from app.servers.routes import servers
    from app.vpnapprovals.routes import vpnapprovals
    from app.vpns.routes import vpns
    from app.approvekinds.routes import approvekinds
    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(departments)
    app.register_blueprint(requesttypes)
    app.register_blueprint(serverapprovals)
    app.register_blueprint(serverrequestgroups)
    app.register_blueprint(serverrights)
    app.register_blueprint(servers)
    app.register_blueprint(vpnapprovals)
    app.register_blueprint(vpns)
    app.register_blueprint(approvekinds)
    return app
