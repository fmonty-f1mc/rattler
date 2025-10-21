from pathlib import Path
import shutil
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from jinja2 import DictLoader
from app.tpls import *

from app.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"

# mail settings
mail = Mail()



def create_app(config_class: object = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)


    # import routes
    from app.main.routes import main
    from app.players.routes import players
    from app.tournaments.routes import tournaments
    from app.divisions.routes import divisions
    
    rts=[main,players,tournaments,divisions]
    
    # create table from models if it doesn't exist
    from app.models import create_table_if_not_exist
    
    app.jinja_loader = DictLoader({'base': tpls["base_tpl"]})

    create_table_if_not_exist(app)

    for bp in rts:
        app.register_blueprint(bp)

    return app