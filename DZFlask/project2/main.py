from flask import Flask, render_template, request, redirect, url_for, session, flash

import os
from pathlib import Path
from datetime import datetime, timedelta
import secrets

#from dotenv import load_dotenv

from extensions import db, migrate, login_manager  # Импортируем db и migrate
from models import Clients, Post, Group, Notes, Users  # Импортируем модели после db!

from flask_login import current_user, login_user, logout_user, login_required


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
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", secrets.token_hex(32))

#login_manager.init_app(app)
#login_manager.login_view = 'login'

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

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST" and 'login_submit' in request.form:
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Все поля обязательны для заполнения!", "error")
            return redirect(url_for("index"))

        user = Users.query.filter_by(username=username).first()

        if user and user.check_password(password):
            auth_token = user.generate_auth_token()
            session['user_id'] = user.id
            session['user_name'] = user.username
            session['token'] = auth_token
            db.session.commit()
            flash("Вы успешно вошли в систему!", "success")
            return redirect(url_for("index"))

        flash("Неверные учетные данные!", "error")
        return redirect(url_for("index"))

    #name = "Григорий"
    return render_template("index.html") # ("index.html", name=name)

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
        client_id = request.form.get("client_id")

        if not all([title, text]):
            return render_template("notes.html",
                                   notes=Notes.query.all(),
                                   error="Заголовок и текст должны быть заполнены")
        with app.app_context():
            # Проверяем существует ли пользователь
            client = Clients.query.get(client_id)
            if not client:
                return render_template("notes.html",
                                       notes=Notes.query.all(),
                                       error=f"Пользователь с ID {client_id} не существует")
            note = Notes(title=title, text=text, client_id=client_id)
            db.session.add(note)
            db.session.commit()

            return redirect(url_for("notes"))

    return render_template("notes.html", notes=Notes.query.all())


@app.route("/client_form", methods=["GET", "POST"])
def client_form():
    return render_template("client_form.html",
                           clients=Clients.query.all(),
                           posts=Post.query.all())

@app.route("/add_client_form", methods=["GET", "POST"])
def add_client_form():
    if request.method == "POST":
        name = request.form.get("name")
        contact = request.form.get("contact")
        info = request.form.get("info")

        if not all([name, contact]):
            return render_template("client_form.html",
                                   clients=Clients.query.all(),
                                   posts=Post.query.all(),
                                   error="Имя и контакт обязательны для заполнения")

        with app.app_context():
            existing_client = Clients.query.filter_by(contact=contact).first()
            if existing_client:
                return render_template("client_form.html",
                                       clients=Clients.query.all(), posts=Post.query.all(),
                                       error=f"Пользователь с контактом {contact} уже существует")

            client = Clients(name=name, contact=contact, info=info)
            db.session.add(client)
            db.session.commit()

            return redirect(url_for("client_form"))

    return render_template("client_form.html",
                           clients=Clients.query.all(), posts=Post.query.all())

@app.route("/add_post_form", methods=["POST"])
def add_post_form():
    title = request.form.get("title")
    content = request.form.get("content")
    client_id = request.form.get("client_id")

    if not all([title, content, client_id]):
        return render_template("client_form.html",
                               clients=Clients.query.all(),
                               posts=Post.query.all(),
                               error="Все поля поста обязательны для заполнения")

    with app.app_context():
        # Проверяем существует ли пользователь
        client = Clients.query.get(client_id)
        if not client:
            return render_template("client_form.html",
                                   clients=Clients.query.all(),
                                   posts=Post.query.all(),
                                   error=f"Пользователь с ID {client_id} не существует")

        post = Post(title=title, content=content, client_id=client_id)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for("client_form"))

@app.route("/add_group")
def add_group():
    client = Clients(name='Victoria', contact='Victoria@Zaiushnica.com', info='prime_user')
    db.session.add(client)
    db.session.commit()
    group = Group(title="it")
    db.session.add(group)
    db.session.commit()
    client.groups = [group]
    db.session.commit()
    """
    Получаем данные из БД
    client = Clients.query.all()
    for client in clients:
        print(client.id, client.username, client.contact)
    return ''
    """
    return ""

@app.route("/registry", methods=["GET", "POST"])
def registry():
    if request.method == "GET":
        return render_template("registry.html")
    else:
        # Проверка паролей
        if request.form["password"] != request.form.get("confirm_password", ""):
            flash("Пароли не совпадают", "Ошибка!")
            return redirect(url_for("registry"))

        existing_user = Users.query.filter_by(email=request.form["email"]).first()
        if existing_user:
            flash("Пользователь с таким email уже существует", "Ошибка!")
            return redirect(url_for("registry"))

        user = Users(username=request.form["user_name"],
                            email=request.form["email"])# , password=request.form["password"]
        user.set_password(request.form["password"])

        db.session.add(user)
        db.session.commit()
        flash("Пользователь успешно зарегистрирован")
        return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        flash("Все поля обязательны для заполнения!")
        return redirect(url_for("login"))

    user = Users.query.filter_by(email=email).first()

    if user and user.check_password(password):
        # Генерируем токен с временем жизни
        auth_token = user.generate_auth_token()
        # Сохраняем в сессии
        session['user_id'] = user.id
        session['user_name'] = user.username
        session['token'] = auth_token

        db.session.commit()

        flash("Вы успешно вошли в систему!", "success")
        return redirect(url_for("index"))
    flash("Неверный email или пароль!", "error")
    return redirect(url_for("login"))

@app.route("/logout", methods=["GET", "POST"])
def logout():
    # Очищаем сессию
    session.pop("user_id", None)
    session.pop("token", None)
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("index"))

@app.before_request
def check_auth():
    if request.endpoint in ['login', 'static', 'registry', 'index', 'logout']:
        return None

    if 'user_id' not in session or 'token' not in session:
        return redirect(url_for('login'))

    user = Users.query.get(session['user_id'])

    if not user or user.token != session.get('token') or \
            user.token_expiration < datetime.utcnow():
        session.clear()
        flash("Сессия истекла")
        return redirect(url_for('login'))

    return None

"""
для этого метода включить элементы со #, в начале файла 
в index.html, в цикле под <h1>Добро пожаловать!</h1>, использовать "{% if current_user.is_authenticated %}"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Обновите маршруты:
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == "POST":
        user = Users.query.filter_by(email=request.form['email']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверные учетные данные')
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))
"""

@app.route("/dell")
def dell_us():
    user = Users(id=1)
    db.session.delete(user)
    db.session.commit()
    return ""


if __name__ == "__main__":
    print("Точный путь к БД:", os.path.abspath('flask.db'))
    init_db()
    app.run(debug=True)