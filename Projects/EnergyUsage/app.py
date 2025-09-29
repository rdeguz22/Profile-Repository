from flask import Flask, render_template, request, redirect, url_for
from db import get_connection

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/logs")
def logs():
    c = get_connection()
    logs = c.execute("SELECT * FROM energy_logs").fetchall()
    c.close()
    return render_template("logs.html", logs=logs)

@app.route("/add_log", methods=["POST"])
def add_log():
    user_id = 1
    log_date = request.form["log_date"]
    category = request.form["category"]
    amount = request.form["amount"]
    unit = request.form["unit"]

    c = get_connection()
    c.execute("""INSERT INTO energy_logs (user_id, log_date, category, amount, unit)
                    VALUES (?, ?, ?, ?, ?)""", (user_id, log_date, category, amount, unit))
    c.commit()
    c.close()

    return redirect(url_for("logs"))

@app.route("/goals")
def goals():
    c = get_connection()
    goals = c.execute("SELECT * FROM goals").fetchall()
    c.close()
    return render_template("goals.html", goals=goals)

@app.route("/add_goal", methods=["POST"])
def add_goal():
    user_id = 1 
    category = request.form["category"]
    target_amount = request.form["target_amount"]
    deadline = request.form["deadline"]

    c = get_connection()
    c.execute("""INSERT INTO goals (user_id, category, target_amount, deadline)
                    VALUES (?, ?, ?, ?)""", (user_id, category, target_amount, deadline))
    c.commit()
    c.close()

    return redirect(url_for("goals"))

if __name__ == "__main__":
    app.run(debug=True)
