from flask import render_template, redirect, url_for, request, g, session
from app import webapp, login_required, get_db
from pymysql import escape_string

import gc
import os


@webapp.route("/gallery")
@login_required
def gallery():
    error = ""
    try:
        cnx = get_db()
        cursor = cnx.cursor()

        APP_RELATED = 'images/' + session['username']

        cursor.execute("SELECT userID FROM users WHERE username = (%s)",
                       (escape_string(session['username'])))
        uID = cursor.fetchone()[0]

        cursor.execute("SELECT pName FROM images WHERE users_userID = (%s)",
                       (int(uID)))
        imagenames = cursor.fetchall()
        images = []
        for imagename in imagenames:
            images.append(APP_RELATED + '/' + imagename[0])

        return render_template("thumbnail-gallery.html", title="Gallery", images=images)

    except Exception as e:
        return str(e)


@webapp.route("/gallery/<path:image>")
@login_required
def full_image(image):
    return render_template("full-image.html", image=image)