from flask import render_template, redirect, url_for, request, g
from app import webapp
from app.config import db_config

import pymysql.cursors

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

@webapp.route("/sign-up-login-form", methods=['GET', 'POST'])
def sign_up_login_form():
    # cnx = get_db()
    #
    # cursor = cnx.cursor()
    #
    # query = ""
    #
    # cursor.execute(query)

    return render_template("form.html", title='Login or Sign up')