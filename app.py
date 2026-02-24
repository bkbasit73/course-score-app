from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///grades.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

GRADE_ITEMS = ["Lab 1", "Lab 2", "Lab 3", "Lab 4", "Lab 5", "Lab 6", "Midterm", "Final", "Project"]

# Midterm 20%, Labs total 30% (6 labs => 5% each), Project 20%, Final 30%
WEIGHTS = {
    "Midterm": 0.20,
    "Final": 0.30,
    "Project": 0.20,
    "Lab 1": 0.05,
    "Lab 2": 0.05,
    "Lab 3": 0.05,
    "Lab 4": 0.05,
    "Lab 5": 0.05,
    "Lab 6": 0.05,
}

def letter_grade(percent: float) -> str:
    if percent >= 90: return "A+"
    if percent >= 85: return "A"
    if percent >= 80: return "A-"
    if percent >= 75: return "B+"
    if percent >= 70: return "B"
    if percent >= 65: return "C+"
    if percent >= 60: return "C"
    if percent >= 50: return "D"
    return "F"

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Float, nullable=False)

# Fix "Working outside of application context"
with app.app_context():
    db.create_all()

def calculate_final(grades):
    scores = {g.item: g.score for g in grades}
    total = 0.0
    for item, w in WEIGHTS.items():
        s = scores.get(item, 0.0)
        total += (s / 100.0) * (w * 100.0)
    return round(total, 2)

@app.route("/", methods=["GET"])
def index():
    grades = Grade.query.order_by(Grade.id.desc()).all()
    final_percent = calculate_final(grades)
    final_letter = letter_grade(final_percent)
    return render_template(
        "index.html",
        grades=grades,
        grade_items=GRADE_ITEMS,
        final_percent=final_percent,
        final_letter=final_letter,
        weights=WEIGHTS,
    )

@app.route("/add", methods=["POST"])
def add():
    item = request.form.get("item")
    score = request.form.get("score")

    if item not in GRADE_ITEMS:
        return redirect(url_for("index"))

    try:
        score_val = float(score)
        if not (0 <= score_val <= 100):
            return redirect(url_for("index"))
    except:
        return redirect(url_for("index"))

    db.session.add(Grade(item=item, score=score_val))
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete/<int:grade_id>", methods=["POST"])
def delete(grade_id):
    g = Grade.query.get_or_404(grade_id)
    db.session.delete(g)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/edit/<int:grade_id>", methods=["POST"])
def edit(grade_id):
    g = Grade.query.get_or_404(grade_id)
    item = request.form.get("item")
    score = request.form.get("score")

    if item in GRADE_ITEMS:
        g.item = item

    try:
        score_val = float(score)
        if 0 <= score_val <= 100:
            g.score = score_val
    except:
        pass

    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)