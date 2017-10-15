from flask import render_template, redirect, url_for, request, g, session, flash
from app import webapp, login_required, get_db, teardown_db
from pymysql import escape_string

import gc
import os


# page for the thumbnail gallery
@webapp.route("/gallery")
@login_required
def gallery():
    error = ""
    try:
        # access database
        cnx = get_db()
        cursor = cnx.cursor()

        # file path of images
        APP_RELATED = 'images/' + session['username']

        # fetch names of the images owned by user
        cursor.execute("SELECT userID FROM users WHERE username = (%s)",
                       (escape_string(session['username'])))
        uID = cursor.fetchone()[0]
        cursor.execute("SELECT pName FROM images WHERE users_userID = (%s)",
                       (int(uID)))
        imagenames = cursor.fetchall()

        # store image paths and pass to frontend
        images = []
        for imagename in imagenames:
            images.append(APP_RELATED + '/' + imagename[0])

        #cleanup
        cursor.close()
        cnx.close()
        return render_template("thumbnail-gallery.html", title="Gallery", images=images)

    except Exception as e:
        teardown_db(e)
        return str(e)


# page for showing full images
@webapp.route("/gallery/<username>/<path:image>")
@login_required
def full_image(username, image):
    try:
        # verify the identity of the user
        pathname = str(image).split('/')
        if not username == pathname[1] or not username == session['username']:
            flash("access denied")
            return redirect(url_for('gallery'))

        # initialize the image list
        images = []
        images.append(image)

        # access to database
        cnx = get_db()
        cursor = cnx.cursor()

        # fetch names of the transformed images
        cursor.execute("SELECT tpName FROM images, trimages WHERE pName=(%s) AND pID=images_pID",
                       (escape_string(pathname[-1])))
        imagenames = cursor.fetchall()

        # store image paths and pass to frontend
        APP_RELATED = 'images/' + session['username']
        for imagename in imagenames:
            images.append(APP_RELATED + '/' + imagename[0])

        # cleanup
        cursor.close()
        cnx.close()
        return render_template("full-image.html", username=username, images=images)

    except Exception as e:
        teardown_db(e)
        return str(e)