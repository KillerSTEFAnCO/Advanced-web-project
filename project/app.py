from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_mysqldb import MySQL, MySQLdb
import bcrypt

app = Flask(__name__)

# Connecting to the Database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'queens_kings_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


app.secret_key = "c2^4bpnxTuGC%FaQyc@D7W!YKw!gb5e37Vbjv8XWpr@yqVem&$XMVh*x&ynb"
# how long to be the session
app.permanent_session_lifetime = timedelta(minutes=60)

# routs for all of the pages


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard/<user>")
def dashboard():
    return render_template("index.html")


@app.route("/aboutus/")
def aboutus():
    return render_template("aboutus.html")


@app.route("/login/", methods=["POST", "GET"])
def login():
    # it the user is already logedin go to homepage/index page
    if "name" in session:
        return redirect(url_for("home"))
    # if user is not logged in take username and passoword from form
    if request.method == "POST":
        username = request.form["username"]
        password = request.form['password'].encode('utf-8')
    # go to the database and find a username that maches the username from the form
    # get one and put it in the object user
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = curl.fetchone()
        curl.close()
    # if username from form doesn't match a username from database
        if user == None:
            flash("Invalid Username", "error")
            return render_template("login.html")
    # if a username matches a username from the database the length of user will be greater then 0
        if len(user) > 0:
            # bcrypt decrypt the password from database and match it with the one from the form if match start session and redirect to the home/index page
            if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
                session.permanent = True
                session['name'] = user['username']
                return redirect(url_for("home"))
            # if pasword doesn't match flash a message and render template login.html
            else:
                flash("Invalid Password", "error")
                return render_template("login.html")
        else:
            return redirect(url_for("home"))
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    # when logout end session
    session.clear()
    return redirect(url_for("home"))


@app.route("/createaccount/", methods=["POST", "GET"])
def createAcc():
    # if user is in session they cant visit the Create Account Page, they will be send to the home/index page
    # Even if they try to manipolate the url
    if "name" in session:
        return redirect(url_for("home"))
    if request.method == 'GET':
        return render_template("createaccount.html")
    else:
        # get the username age and password for the html for
        name = request.form['username']
        age = request.form['age']
        password = request.form['password'].encode('utf-8')
        # hash the password
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        # connect the the database and insert the new user
        # Ignore if there is already an existing username that is the same
        cur = mysql.connection.cursor()
        cur.execute("INSERT IGNORE INTO users (username, age, PASSWORD) VALUES (%s,%s,%s)",
                    (name, age, hash_password,))
        mysql.connection.commit()
        session['username'] = request.form['username']
        return redirect(url_for('login'))


@app.route("/puzzle/")
def puzzle():
    # allow only logged in users to visit it
    if 'name' in session:
        return render_template("puzzles.html")
    else:
        # if user is not logged take them to the login page and show them the message
        flash('You need to Login')
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
