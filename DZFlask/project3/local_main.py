from flask import Flask, jsonify, request, abort

import secrets
import os
from pathlib import Path

from models import Users
from extensions import db

app = Flask(__name__)

current_dir = Path(__file__).parent # Это даст C:\Users\...\project
db_path = current_dir / "instance" / "flask.db"
os.makedirs(current_dir / "instance", exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", secrets.token_hex(32))

db.init_app(app)

new_notes = [
    {"topic": "rest api"},
    {"new": "test"}
]

@app.route("/api/get/<int:new_notes_index>")
def get_tasks(new_notes_index):
    # Если ввести в поиск "сайт"/api/get/0 --->>> {"topic": "rest api"}
    # Если ввести в поиск "сайт"/api/get/1 --->>> {"new": "test"}
    return new_notes[new_notes_index]
@app.route("/api/task", methods=["POST"])
def add_new_note():
    new_note = {"new": "!!!NEW_TEST!!!"}
    new_notes.append(new_note)
    return jsonify({"new_note": new_note}), 201
# В начале нужно запустить main
# curl.exe -i -H "Content-Type: application/json" -X POST http://localhost:5000/api/task
# curl.exe -i -H "Content-Type: application/json" -X POST -d '{"new": "!!!NEW_TEST!!!"}' http://localhost:5000/api/task

@app.route("/api/delete/<int:to_delete>")
def del_note(to_delete):
    del new_notes[to_delete]
    return new_notes

@app.route("/api/put/<int:to_edit>")
def edit_note(to_edit):
    user = db.session.query(Users).filter_by(id=to_edit).first()
    if not user:
        abort(404, description="User not found")

    data = request.get_json()
    if not data:
        abort(400, description="No JSON data provided")

    # Разрешённые поля для обновления (защита от Mass Assignment)
    allowed_fields = {"name", "email", "age"}  # Пример: только эти поля можно менять
    updates = {k: v for k, v in data.items() if k in allowed_fields}

    for k,v in updates.items():
        setattr(user, k, v)
    db.session.commit()
    return user.to_dic(), 201


"""
if __name__ == "__main__":
    app.run(debug=True)
"""