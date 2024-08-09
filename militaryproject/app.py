import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure trainer.db to use SQLite database
db = SQL("sqlite:///trainer.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    """Show homepage"""

    rows = db.execute ("SELECT first_name FROM users WHERE id = :user_id", user_id=session["user_id"])
    first_name = rows[0]["first_name"]

    # Render index.html
    return render_template("index.html", first_name=first_name)

@app.route("/library")
@login_required
def library():
    """Show TTG Library"""

    # Render library.html
    return render_template("library.html")

@app.route("/dashboard")
@login_required
def dashboard():
    """Show every user's certification"""

    rows = db.execute("""SELECT
    users.username,
    users.first_name,
    users.last_name,
    MAX(CASE WHEN completed.description = 'Air Transportation' THEN completed.timestamp END) AS task_1_timestamp,
    MAX(CASE WHEN completed.description = 'Career Progression' THEN completed.timestamp END) AS task_1_1_timestamp,
    MAX(CASE WHEN completed.description = 'Organizational Structure' THEN completed.timestamp END) AS task_1_2_timestamp,
    MAX(CASE WHEN completed.description = 'Types and Descriptions of Transport Aircrafts' THEN completed.timestamp END) AS task_1_3_timestamp,
    MAX(CASE WHEN completed.description = 'Locate and Reference Transportation Forms, Publications, and Technical Orders' THEN completed.timestamp END) AS task_1_4_timestamp,
    MAX(CASE WHEN completed.description = 'Inspect, Inventory, and Store 463L Pallets, Nets, and Tie Down Equipment' THEN completed.timestamp END) AS task_1_5_timestamp,
    MAX(CASE WHEN completed.description = 'Build Single Pallet' THEN completed.timestamp END) AS task_1_6_timestamp,
    MAX(CASE WHEN completed.description = 'Identify Types of Shoring' THEN completed.timestamp END) AS task_1_7_timestamp,
    MAX(CASE WHEN completed.description = 'Perform Spotter - Chocker Duties' THEN completed.timestamp END) AS task_1_8_timestamp,
    MAX(CASE WHEN completed.description = 'Vehicle Inspections' THEN completed.timestamp END) AS task_1_9_timestamp,
    MAX(CASE WHEN completed.description = 'Perform Engine Running Off-load On-load (ERO) Operations' THEN completed.timestamp END) AS task_1_10_timestamp,
    MAX(CASE WHEN completed.description = 'Air Transportation Information Systems' THEN completed.timestamp END) AS task_1_11_timestamp,
    MAX(CASE WHEN completed.description = 'Compliance-Evaluation Fundamentals' THEN completed.timestamp END) AS task_1_12_timestamp
FROM
    users
LEFT JOIN
    completed ON users.id = completed.user_id
GROUP BY
    users.username, users.first_name, users.last_name""")

    # Render dashboard.html
    return render_template("dashboard.html", rows=rows)

@app.route("/progress")
@login_required
def progress():
    """Show Certified Tasks"""

    rows = db.execute("SELECT * FROM completed WHERE user_id = :user_id", user_id=session["user_id"])

    # Render library.html
    return render_template("progress.html", rows=rows)

@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    # Get username
    username = request.args.get("username")

    # Check for username
    if not len(username) or db.execute("SELECT 1 FROM users WHERE username = :username", username=username):
        return jsonify(False)
    else:
        return jsonify(True)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out."""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user for an account."""

    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("username"):
            return apology("missing username")
        elif not request.form.get("password"):
            return apology("missing password")
        elif not request.form.get("firstname"):
            return apology("missing first name")
        elif not request.form.get("lastname"):
            return apology("missing last name")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match")

        # Add user to database
        try:
            id = db.execute("INSERT INTO users (username, hash, first_name, last_name) VALUES(?, ?, ?, ?)",
                            request.form.get("username"),
                            generate_password_hash(request.form.get("password")),
                            request.form.get("firstname"),
                            request.form.get("lastname"))
        except ValueError:
            return apology("username taken")

        # Log user in
        session["user_id"] = id

        # Let user know they're registered
        flash("Registered!")
        return redirect("/")

    # GET
    else:
        return render_template("register.html")

@app.route("/sign", methods=["GET", "POST"])
@login_required
def sign():

    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("task"):
            return apology("missing task")
        if not request.form.get("prereq"):
            return apology("Complete Prerequisites before signing")
        if not request.form.get("cbt"):
            return apology("Complete Computer Based Training before signing")
        if not request.form.get("tec"):
            return apology("Complete Task Evaluation Checklist before Proceeding")
        
        # Add the task in completed
        db.execute("INSERT INTO completed (user_id, description, timestamp) VALUES(:user_id, :description, CURRENT_TIMESTAMP)", 
                   user_id=session["user_id"], description=request.form.get("task"))
        # Display completed tasks
        flash("Signed!")
        return redirect("/")
    # GET
    else:

        # Show tasks in task list
        tasks = db.execute("SELECT description FROM tasks WHERE description NOT IN (SELECT description FROM completed WHERE user_id = ?)", session["user_id"])

        # Display sign
        return render_template("sign.html", tasks=tasks)
    
@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    if request.method == "POST":
        # Ensure password was submitted
        if not request.form.get("confirm_password"):
            return apology("must provide password", 403)

        # Ensure new password was submitted
        elif not request.form.get("new_password"):
            return apology("must provide new password", 403)

        # Ensure password and password confirmation matches
        elif request.form.get("new_password") != request.form.get("confirm_password"):
            return apology("passwords must match", 403)

        # Hash password
        hashed_password = generate_password_hash(request.form.get("confirm_password"))

        # Update new password in database
        db.execute(
            "UPDATE users SET hash = :hashed_password WHERE id = :user_id",
            hashed_password=hashed_password,
            user_id=session["user_id"],
        )

        # After successful registration
        flash("Password Change successful.")
        return redirect("/")

    else:
        return render_template("changepassword.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
