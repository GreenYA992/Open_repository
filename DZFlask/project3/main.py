from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy.orm import load_only

import os
from pathlib import Path
import secrets

# from dotenv import load_dotenv

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

app = Flask(__name__)

current_dir = Path(__file__).parent  # Это даст C:\Users\...\project
db_path = current_dir / "instance" / "flask.db"
os.makedirs(current_dir / "instance", exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", secrets.token_hex(32))

login_manager.init_app(app)
login_manager.login_view = 'login'

# Инициализируем db и migrate
db.init_app(app)
migrate.init_app(app, db)

"""
Команды для миграции (внесение изменений в структуру базы):
1. flask --app main.py db init (создается директория migrations), 
2. flask --app main.py db migrate -m "Initial migration"
3. flask --app main.py db upgrade 
------------------------------------------------------
удаляем старые миграции 'rm -rf ./migrations/' (не получилось),
Через PowerShell от админа Remove-Item -Path "C:/Users/Green/OneDrive/
Рабочий стол/Обучение/Python/New_Project_Code/DZFlask/project/migrations" -Recurse -Force
-------------------------------------------------------
Для работы через терминал: flask --app main.py shell
пример использования print(Notes.query.get(2).user_id)
"""

def init_db():
    with app.app_context():
        db.create_all()
        print("Таблицы созданы!")

""" 
Создаем БД через консоль:
в консоли вводим 'python', далее:
'from main import app, db' далее 'app.app_context().push()' далее 'db.create_all()'
Для выхода из режима 'quit()' 
"""

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route("/protected")
@login_required
def protected():
    return "Только для авторизованных!"

@app.route("/")
def index():
    return render_template("index.html")  # ("index.html", name=name)

@app.route("/table")
def table():
    return render_template("table.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    return f"Привет, {name}"


@app.route("/notes")
@login_required
def notes():
    note = db.session.query(
        Notes.id,
        Notes.user_id,
        Notes.title,
        Notes.text,
        Users.username.label('user_name')  # Это корректно
    ).join(Users).all()
    return render_template("notes.html", notes=note) # =Notes.query.all()
@app.route("/add_note", methods=["GET", "POST"])
@login_required
def add_note():
    if request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")

        if not all([title, text]):
            return render_template("notes.html",
                                   notes=Notes.query.all(),
                                   error="Заголовок и текст должны быть заполнены")
        if current_user.is_authenticated:
            note = Notes(title=title, text=text, user_id=current_user.id)
            db.session.add(note)
            db.session.commit()

            return redirect(url_for("notes"))

    return render_template("notes.html", notes=Notes.query.all())


@app.route("/client_form")
@login_required
def client_form():
    return render_template("client_form.html",
                           clients=Clients.query.all(),
                           posts=Post.query.all())
@app.route("/add_client_form", methods=["POST"])
@login_required
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
        password = request.form["password"].strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        email = request.form["email"].strip()
        username = request.form.get("user_name").strip()

        print(f"Пароль: '{password}', длина: {len(password)}")

        if not password or not confirm_password or not email or not username:
            flash("Все поля обязательны для заполнения!", "error")
            return redirect(url_for("registry"))
        if password != confirm_password:
            flash("Пароли не совпадают", "error")
            return redirect(url_for("registry"))
        if len(password) < 5:
            flash("Пароль не надежный! "
                  "Пароль должен содержать 5 или более символов", "error")
            return redirect(url_for("registry"))
        if Users.query.filter_by(email=email).first():
            flash("Email уже занят", "error")
            return redirect(url_for("registry"))
        if Users.query.filter_by(username=username).first():
            flash("Имя пользователя уже занято", "error")
            return redirect(url_for("registry"))

        existing_user = Users.query.filter_by(email=request.form["email"]).first()
        if existing_user:
            flash("Пользователь с таким email уже существует", "error")
            return redirect(url_for("registry"))

        user = Users(username=username,
                     email=email,
                     is_active=True)  # , password=request.form["password"]
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        flash("Пользователь успешно зарегистрирован", "success")
        return redirect(url_for("login"))

@app.route("/user_panel")
@login_required
def user_panel():
    user = Users.query.options(
        load_only(Users.username, Users.email),  # Только эти поля из Users
        db.joinedload(Users.notes)  # Плюс все заметки
    ).get(current_user.id)
    return render_template("user_panel.html", user=user)
@app.route("/user_change", methods=["GET", "POST"])
@login_required
def change_user_data():
    if request.method == "POST":
        # Получаем данные формы
        username = request.form.get("username")
        email = request.form.get("email")
        current_password = request.form.get("password")
        new_password = request.form.get("new_password")
        confirm_new_pass = request.form.get("confirm_new_password")

        # Проверка текущего пароля
        if not current_user.check_password(current_password):
            flash("Неверный текущий пароль", "error")
            return redirect(url_for("change_user_data"))

        if new_password != confirm_new_pass:
            flash("Пароли не совпадают", "error")
            return redirect(url_for("change_user_data"))

        try:
            # Обновление базовых данных
            current_user.username = username
            current_user.email = email

            # Обновление пароля (если указан новый)
            if new_password:
                current_user.set_password(new_password)  # Используем метод из модели

            db.session.commit()
            flash("Данные успешно обновлены", "success")
            return redirect(url_for("user_panel"))

        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при обновлении: {str(e)}", "error")
            return redirect(url_for("change_user_data"))

    return render_template("user_edit.html", user=current_user)
@app.route("/del_user", methods=["GET", "POST"])
@login_required
def delete_user_data():
    if request.method == "POST":
        # Получаем данные формы
        current_password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not current_password or not confirm_password:
            flash("Все поля обязательны для заполнения", "error")
            return redirect(url_for("delete_user_data"))

        if not current_user.check_password(current_password):
            flash("Неверный текущий пароль", "error")
            return redirect(url_for("delete_user_data"))

        if current_password != confirm_password:
            flash("Пароли не совпадают", "error")
            return redirect(url_for("delete_user_data"))

        try:
            # Удаляем все связанные записи пользователя (заметки)
            Notes.query.filter_by(user_id=current_user.id).delete()

            # Удаляем самого пользователя
            db.session.delete(current_user)
            db.session.commit()

            # Выходим из системы
            logout_user()
            flash("Ваш аккаунт успешно удален", "success")
            return redirect(url_for("index"))

        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при удалении аккаунта: {str(e)}", "error")
            return redirect(url_for("delete_user_data"))

    return render_template("delete_user_confirm.html")


@app.route("/edit_note/<int:note_id>", methods=["GET", "POST"])
@login_required
def edit_note(note_id):
    note = Notes.query.filter_by(id=note_id, user_id=current_user.id).first()

    if not note:
        flash("Заметка не найдена или у вас нет прав на ее изменение", "error")
        return redirect(url_for("user_panel"))

    if request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")

        if not title or not text:
            flash("Заголовок и текст не могут быть пустыми", "error")
        else:
            note.title = title
            note.text = text
            db.session.commit()
            flash("Заметка успешно обновлена", "success")
            return redirect(url_for("user_panel"))

    return render_template("edit_note.html", note=note)
@app.route("/delete_note", methods=["POST"])
@login_required
def delete_note():
    note_id = request.form.get("note_id")
    note = Notes.query.filter_by(id=note_id, user_id=current_user.id).first()

    if note:
        db.session.delete(note)
        db.session.commit()
        flash("Заметка успешно удалена", "success")
    else:
        flash("Заметка не найдена или у вас нет прав на ее удаление", "error")

    return redirect(url_for("user_panel"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "POST":
        user = Users.query.filter_by(email=request.form['email']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверные учетные данные', "error")
    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == "__main__":
    print("Точный путь к БД:", os.path.abspath('flask.db'))
    init_db()
    app.run(debug=True)
