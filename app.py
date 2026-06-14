from flask import Flask, render_template, request, redirect, session
import json

app = Flask(__name__)
app.secret_key = "super_secret_key"


# =====================
# LOAD & SAVE USERS
# =====================
def load_users():
    with open("users.json", "r") as f:
        return json.load(f)


def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)


# =====================
# ROOT ROUTE (IMPORTANT FIX)
# =====================
@app.route("/")
def index():
    return redirect("/login")


# =====================
# HOME (AFTER LOGIN)
# =====================
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("home.html", user=session["user"])


# =====================
# REGISTER PAGE
# =====================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        users = load_users()

        username = request.form["username"]
        password = request.form["password"]
        recovery = request.form["recovery"]

        if username in users:
            return "User already exists"

        users[username] = {
            "password": password,
            "recovery_code": recovery,
            "failed_attempts": 0,
            "locked": False
        }

        save_users(users)

        return redirect("/login")

    return render_template("register.html")


# =====================
# LOGIN PAGE
# =====================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        users = load_users()

        username = request.form["username"]
        password = request.form["password"]

        if username not in users:
            return "User not found"

        if users[username]["locked"]:
            return "Account Locked"

        if users[username]["password"] == password:

            users[username]["failed_attempts"] = 0
            save_users(users)

            session["user"] = username
            return redirect("/home")

        users[username]["failed_attempts"] += 1

        if users[username]["failed_attempts"] >= 3:
            users[username]["locked"] = True

        save_users(users)

        return "Wrong Password"

    return render_template("login.html")


# =====================
# RECOVERY PAGE
# =====================
@app.route("/recover", methods=["GET", "POST"])
def recover():
    if request.method == "POST":

        users = load_users()

        username = request.form["username"]
        recovery = request.form["recovery"]
        new_password = request.form["new_password"]

        if username not in users:
            return "User not found"

        if users[username]["recovery_code"] != recovery:
            return "Wrong Recovery Code"

        users[username]["password"] = new_password
        users[username]["failed_attempts"] = 0
        users[username]["locked"] = False

        save_users(users)

        return redirect("/login")

    return render_template("recover.html")


# =====================
# LOGOUT
# =====================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# =====================
# RUN SERVER
# =====================
if __name__ == "__main__":
    app.run(debug=True)