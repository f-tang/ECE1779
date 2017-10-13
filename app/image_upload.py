from flask import render_template, redirect, url_for, request, g, flash, session
from app import webapp, login_required, get_db
from pymysql import escape_string

import gc
import os


APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@webapp.route('/image-upload', methods=['GET', 'POST'])
@login_required
def image_upload():
    error = ''
    try:
        if request.method == "POST":
            cnx = get_db()
            cursor = cnx.cursor()
            cursor.execute("SELECT userID FROM users WHERE username = (%s)",
                           (escape_string(session['username'])))
            uID = cursor.fetchone()[0]

            APP_RELATED = 'static/images/' + session['username']
            target = os.path.join(APP_ROOT, APP_RELATED)

            if not os.path.isdir(target):
                os.mkdir(target)

            for file in request.files.getlist("file"):
                cursor.execute("SELECT max(pID) FROM images")
                x = cursor.fetchone()
                if x[0] == None:
                    pID = 1;
                else:
                    pID = x[0] + 1

                filename = escape_string(file.filename)
                cursor.execute("INSERT INTO images (pID, pName, users_userID) VALUES (%s, %s, %s)",
                               (int(pID), filename, int(uID)))
                cnx.commit()

                destination = "/".join([target, filename])
                print(destination)
                file.save(destination)

            cursor.close()
            cnx.close()

            gc.collect()

            flash("upload successful")
            return redirect(url_for("gallery"))

        return render_template("image-upload.html", title="upload images")

    except Exception as e:
        return str(e)


