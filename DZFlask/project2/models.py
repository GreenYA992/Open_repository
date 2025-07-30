from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from datetime import datetime, timedelta

"""
load_dotenv("login.env")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
"""

""" 
Создаем БД через консоль: 
'python' --->>>
'from main import app, db' далее 'app.app_context().push()' далее 'db.create_all()'
Для выхода из режима 'quit()'
"""

"""
Команды для миграции:
$env:FLASK_APP = "main.py", проверка, что переменная установлена echo $env:FLASK_APP
далее flask db init (создается директория migrations)
flask db migrate далее flask db upgrade
"""


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String(100))
    token_expiration = db.Column(db.DateTime)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def generate_auth_token(self, expires_in=1800):
        """Генерирует токен с указанным временем жизни (по умолчанию 1 час)"""
        self.token = secrets.token_urlsafe(32)
        self.token_expiration = datetime.utcnow() + timedelta(seconds=expires_in)
        return self.token



class Clients(db.Model):
    # unique=True - каждое имя уникальное, nullable=False - не может быть пустым
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    contact = db.Column(db.String(50), unique=True, nullable=False)
    info = db.Column(db.String(200), nullable=False)

    post = db.relationship("Post", backref="author", lazy="dynamic")
    notes = db.relationship("Notes", backref="author", lazy="dynamic")
    groups = db.relationship("Group", secondary="client_group", backref=db.backref("client", lazy="dynamic"))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200))
    text = db.Column(db.String(200))

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))

client_group = db.Table("client_group",
                      db.Column("clients_id",db.Integer, db.ForeignKey("clients.id")),
                      db.Column("group_id", db.Integer, db.ForeignKey("group.id")))

