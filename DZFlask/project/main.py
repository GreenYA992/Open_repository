from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
_notes = {}

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
    return render_template("notes.html", notes=_notes)

@app.route("/add_note", methods=["POST"])
def add_note():
    title = request.form["title"]
    text = request.form["text"]
    if title and text:
        _notes[title] = text
    return redirect(url_for("notes"))


if __name__ == "__main__":
    app.run(debug=True)
