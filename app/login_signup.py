from flask import render_template, redirect, url_for, request, g, flash, session
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, validators

from passlib.hash import sha256_crypt

from app import webapp, login_required
from app.config import db_config

import pymysql.cursors
from pymysql import escape_string

import gc

# access database
def connect_to_database():
    return pymysql.connect(host=db_config['host'],
                                user=db_config['user'],
                                password=db_config['password'],
                                db=db_config['database'])

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._databse = connect_to_database()
    return db

@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# define login form
class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    password = PasswordField('Password', [validators.DataRequired()])


# login page
@webapp.route("/Login", methods=['GET', 'POST'])
def login_form():
    error = ''
    try:
        form = LoginForm(request.form)
        cnx = get_db()
        cursor = cnx.cursor()
        if request.method == "POST":

            if not form.validate_on_submit():
                error = "request is invalidated"
                return render_template("login-form.html", title='Login', form=form, error=error)

            cursor.execute("SELECT password FROM users WHERE username = (%s)",
                            escape_string(form.username.data))
            x = cursor.fetchone()

            if x == None:
                error = "Username does not exist"
                return render_template("login-form.html", title='Login', form=form, error=error)

            data = x[0]
            if sha256_crypt.verify(form.password.data, data):
                session['logged_in'] = True
                session['username'] = form.username.data

                flash("You are now logged in")
                return redirect(url_for("main"))
            else:
                error = "Invalid credentials, try again."
                return render_template("login-form.html", title='Login', form=form, error=error)

        gc.collect()
        return render_template("login-form.html", title='Login', form=form, error=error)

    except Exception as e:
        return str(e)


# define sign up form
class SignUpForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    email = StringField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm', message="Password must match")])
    confirm = PasswordField('Repeat Password')

    accept_tos = BooleanField('I accept the <a href="/tos"> Terms of Service</a> '
                              'and the <a href="/privacy"> Privacy Notice</a>', [validators.DataRequired()])


# signup page
@webapp.route("/Signup", methods=['GET', 'POST'])
def signup_form():
    error = ''
    try:
        form = SignUpForm(request.form)

        if request.method == "POST":

            if not form.validate_on_submit():
                error = "request is invalidated"
                return render_template("signup-form.html", title='sign up', form=form, error=error)

            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))

            cnx = get_db()
            cursor = cnx.cursor()
            cursor.execute("SELECT * FROM users WHERE username = (%s)",
                           (escape_string(username)))
            x = cursor.fetchone()

            if not x == None:
                error = "That username is already taken"
                return render_template('signup-form.html', title='sign up', form=form, error=error)
            else:
                cursor.execute("SELECT max(userID) AS max_value FROM users")
                uid = x[0] + 1
                cursor.execute("INSERT INTO users (userID, username, password, email) VALUES (%s, %s, %s, %s)",
                               (int(uid), escape_string(username), escape_string(password), escape_string(email)))
                cnx.commit()

                flash("Thanks for signing up!")
                cursor.close()
                cnx.close()

                gc.collect()

                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('main'))

        return render_template("signup-form.html", title='sign up', form=form, error=error)

    except Exception as e:
        return str(e)


# logout page
@webapp.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('main'))

