from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()  # Создаём экземпляр db
migrate = Migrate()  # Пока без привязки к app
