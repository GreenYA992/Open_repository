from extensions import db

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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """"""
    name = db.Column(db.String(50), unique=False, nullable=False)
    # unique=True - каждое имя уникальное, nullable=False - не может быть пустым
    contact = db.Column(db.String(50), unique=True, nullable=False)
    info = db.Column(db.String(200), nullable=False)
    post = db.relationship("Post", backref="author", lazy="dynamic")
    notes = db.relationship("Notes", backref="author", lazy="dynamic")
    groups = db.relationship("Group", secondary="user_group", backref=db.backref("users", lazy="dynamic"))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200))
    text = db.Column(db.String(200))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))

user_group = db.Table("user_group",
                      db.Column("user_id",db.Integer, db.ForeignKey("user.id")),
                      db.Column("group_id", db.Integer, db.ForeignKey("group.id")))
