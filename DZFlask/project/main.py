from flask import Flask, render_template, request, redirect, url_for

import os
from pathlib import Path
#from dotenv import load_dotenv

from extensions import db, migrate  # Импортируем db и migrate
from models import User, Post, Group, Notes  # Импортируем модели после db!

"""
load_dotenv("login.env")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
"""

""" 
Создаем БД через консоль:
в консоли вводим 'python', далее:
'from main import app, db' далее 'app.app_context().push()' далее 'db.create_all()'
Для выхода из режима 'quit()' 
"""

app = Flask(__name__)
"""
db_path = Path("C:/Users/Green/OneDrive/Рабочий стол/Обучение"
               "/Python/New_Project_Code/DZFlask/project/instance")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}/flask.db" # "sqlite:///flask.db"
"""
current_dir = Path(__file__).parent # Это даст C:\Users\...\project
db_path = current_dir / "instance" / "flask.db"
os.makedirs(current_dir / "instance", exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

# Инициализируем db и migrate
db.init_app(app)
migrate.init_app(app, db)

"""
Команды для миграции (внесение изменений в структуру базы):
1. flask --app main.py db init (создается директория migrations), 
2. flask --app main.py db migrate -m "Initial migration"
3. flask --app main.py db upgrade 
удаляем старые миграции 'rm -rf ./migrations/' (не получилось),
Через PowerShell от админа Remove-Item -Path "C:/Users/Green/OneDrive/Рабочий стол/Обучение/Python/New_Project_Code/DZFlask/project/migrations" -Recurse -Force
"""

dict_notes = {}

def init_db():
    with app.app_context():
        db.create_all()
        print("Таблицы созданы!")

@app.route("/")
def index():
    name = "Григорий"
    return render_template("index.html", name=name)

@app.route("/table")
def table():
    return render_template("table.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    return f"Привет, {name}"

@app.route("/notes")
def notes():
    return render_template("notes.html", notes=Notes.query.all())
    # dict_notes=dict_notes, (словарь)

@app.route("/add_note", methods=["GET", "POST"])
def add_note():
    """
    !!!Добавление данных в словарик!!!
    title = request.form["title"]
    text = request.form["text"]
    if title and text:
        dict_notes[title] = text
    """
    if request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")
        user_id = request.form.get("user_id")

        if not all([title, text]):
            return render_template("notes.html",
                                   notes=Notes.query.all(),
                                   error="Заголовок и текст должны быть заполнены")
        with app.app_context():
            # Проверяем существует ли пользователь
            user = User.query.get(user_id)
            if not user:
                return render_template("notes.html",
                                       notes=Notes.query.all(),
                                       error=f"Пользователь с ID {user_id} не существует")
            note = Notes(title=title, text=text, user_id=user_id)
            db.session.add(note)
            db.session.commit()

            return redirect(url_for("notes"))

    return render_template("notes.html", notes=Notes.query.all())

@app.route("/add_user")
def add_user():
    """
    Добавляем запись в БД
    """
    print("Текущий путь к БД:", app.config["SQLALCHEMY_DATABASE_URI"])
    with app.app_context():
        user = User(name='Ivan', contact='ivan@ivanovich.com', info='new_user')
        db.session.add(user)
        db.session.commit()
        """
        Получаем данные из БД
        user = User.query.all()
        for user in users:
            print(user.id, user.username, user.contact)
        return ''
        """
        return ""


@app.route("/add_post")
def add_post():
    post = Post(title="Урок по БД", content="Миграция БД", user_id=1) # author=user
    db.session.add(post)
    db.session.commit()
    return ""

@app.route("/user_form", methods=["GET", "POST"])
def user_form():
    return render_template("user_form.html", users=User.query.all(), posts=Post.query.all())

@app.route("/add_user_form", methods=["GET", "POST"])
def add_user_form():
    if request.method == "POST":
        name = request.form.get("name")
        contact = request.form.get("contact")
        info = request.form.get("info")

        if not all([name, contact]):
            return render_template("user_form.html",
                                   users=User.query.all(),
                                   posts=Post.query.all(),
                                   error="Имя и контакт обязательны для заполнения")

        with app.app_context():
            existing_user = User.query.filter_by(contact=contact).first()
            if existing_user:
                return render_template("user_form.html",
                                       users=User.query.all(), posts=Post.query.all(),
                                       error=f"Пользователь с контактом {contact} уже существует")

            user = User(name=name, contact=contact, info=info)
            db.session.add(user)
            db.session.commit()

            return redirect(url_for("user_form"))

    return render_template("user_form.html",
                           users=User.query.all(), posts=Post.query.all())

@app.route("/add_post_form", methods=["POST"])
def add_post_form():
    title = request.form.get("title")
    content = request.form.get("content")
    user_id = request.form.get("user_id")

    if not all([title, content, user_id]):
        return render_template("user_form.html",
                               users=User.query.all(),
                               posts=Post.query.all(),
                               error="Все поля поста обязательны для заполнения")

    with app.app_context():
        # Проверяем существует ли пользователь
        user = User.query.get(user_id)
        if not user:
            return render_template("user_form.html",
                                   users=User.query.all(),
                                   posts=Post.query.all(),
                                   error=f"Пользователь с ID {user_id} не существует")

        post = Post(title=title, content=content, user_id=user_id)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for("user_form"))

@app.route("/add_group")
def add_group():
    user = User(name='Victoria', contact='Victoria@Zaiushnica.com', info='prime_user')
    db.session.add(user)
    db.session.commit()
    group = Group(title="it")
    db.session.add(group)
    db.session.commit()
    user.groups = [group]
    db.session.commit()
    return ""

if __name__ == "__main__":
    print("Точный путь к БД:", os.path.abspath('flask.db'))
    init_db()
    app.run(debug=True)
