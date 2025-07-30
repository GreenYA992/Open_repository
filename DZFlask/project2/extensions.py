from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_login import LoginManager

db = SQLAlchemy()  # Создаём экземпляр db
migrate = Migrate()  # Пока без привязки к app
login_manager = LoginManager()