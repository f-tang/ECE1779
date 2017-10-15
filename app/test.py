from flask import render_template, redirect, url_for, request, g, flash, session
from app import webapp, get_db
from pymysql import escape_string
from passlib.hash import sha256_crypt
from wand.image import Image

import gc
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


def image_transfer(imagefile, method):
    try:
        if int(method) == 0:
            imagefile.flip()
        if int(method) == 1:
            imagefile.evaluate(operator='rightshift', value=1, channel='blue')
            imagefile.evaluate(operator='leftshift', value=1, channel='red')
        if int(method) == 2:
            imagefile.type = 'grayscale'
        return imagefile
    except Exception as e:
        return str(e)


@webapp.route("/test/FileUpload", methods=['GET', 'POST'])
def test_fileupload():
    error = ""
    try:
        if request.method == 'POST':
            username = request.form["userID"]
            password = request.form["password"]

            cnx = get_db()
            cursor = cnx.cursor()

            cursor.execute("SELECT password FROM users WHERE username = (%s)",
                           (escape_string(username)))
            x = cursor.fetchone()

            if x == None:
                error = "Invalid credentials, try again."
                return render_template("test-form.html", error=error)

            data = x[0]
            if not sha256_crypt.verify(password, data):
                error = "Invalid credentials, try again."
                return render_template("test-form.html", error=error)

            if 'uploadedfile' not in request.files:
                error = "file does not exist"
                return render_template("test-form.html", error=error)
            
            file = request.files['uploadedfile']
            if file == None or file.filename == '':
                error = "file does not exist"
                return render_template("test-form.html", error=error)

            cursor.execute("SELECT userID FROM users WHERE username = (%s)",
                           (escape_string(username)))
            uID = cursor.fetchone()[0]
            APP_RELATED = 'static/images/' + escape_string(username)
            target = os.path.join(APP_ROOT, APP_RELATED)
            if not os.path.isdir(target):
                os.mkdir(target)

            cursor.execute("SELECT max(pID) FROM images")
            x = cursor.fetchone()
            if x[0] == None:
                pID = 1;
            else:
                pID = x[0] + 1

            filename = escape_string(str(pID) + file.filename)
            destination = "/".join([target, filename])
            file.save(destination)

            cursor.execute("INSERT INTO images (pID, pName, users_userID) VALUES (%s, %s, %s)",
                           (int(pID), filename, int(uID)))

            for i in range(3):
                cursor.execute("SELECT max(tpID) FROM trimages")
                x = cursor.fetchone()
                if x[0] == None:
                    tpID = 1;
                else:
                    tpID = x[0] + 1

                tfilename = escape_string("tr" + str(i) + "_" + filename)
                img = Image(filename=destination)
                with img.clone() as tfile:
                    image_transfer(tfile, i)
                    tdestination = "/".join([target, tfilename])
                    tfile.save(filename=tdestination)
                    cursor.execute("INSERT INTO trimages (tpID, tpName, images_pID) VALUES (%s, %s, %s)",
                                   (int(tpID), tfilename, int(pID)))

            cnx.commit()
            cursor.close()
            cnx.close()

            gc.collect()

            flash("upload successful")
            return redirect(url_for("test_fileupload"))

        return render_template("test-form.html")

    except Exception as e:
        return str(e)
