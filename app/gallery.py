from flask import render_template, redirect, url_for, request, g, session, flash
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


        cursor.close()
        cnx.close()
        return render_template("thumbnail-gallery.html", title="Gallery", images=images)

    except Exception as e:
        return str(e)


@webapp.route("/gallery/<username>/<path:image>")
@login_required
def full_image(username, image):
    try:
        pathname = str(image).split('/')
        if not username == pathname[1] or not username == session['username']:
            flash("access denied")
            return redirect(url_for('gallery'))

        images = []
        images.append(image)

        cnx = get_db()
        cursor = cnx.cursor()

        cursor.execute("SELECT tpName FROM images, trimages WHERE pName=(%s) AND pID=images_pID",
                       (escape_string(pathname[-1])))
        imagenames = cursor.fetchall()

        APP_RELATED = 'images/' + session['username']
        for imagename in imagenames:
            images.append(APP_RELATED + '/' + imagename[0])

        cursor.close()
        cnx.close()
        return render_template("full-image.html", username=username, images=images)

    except Exception as e:
        return str(e)