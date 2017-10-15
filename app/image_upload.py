from flask import render_template, redirect, url_for, request, g, flash, session
from app import webapp, login_required, get_db,teardown_db
from pymysql import escape_string
from wand.image import Image

import gc
import os

# get the absolute path of the file
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# implement image transformation
def image_transfer(imagefile, method):
    try:
        if int(method) == 0:
            # flip image
            imagefile.flip()
        if int(method) == 1:
            # color shift
            imagefile.evaluate(operator='rightshift', value=1, channel='blue')
            imagefile.evaluate(operator='leftshift', value=1, channel='red')
        if int(method) == 2:
            # gray scale
            imagefile.type = 'grayscale'
        return imagefile
    except Exception as e:
        return str(e)

# page for image upload
@webapp.route('/image-upload', methods=['GET', 'POST'])
@login_required
def image_upload():
    error = ''
    try:
        if request.method == "POST":
            # access to database
            cnx = get_db()
            cursor = cnx.cursor()

            # fetch the user ID of user
            cursor.execute("SELECT userID FROM users WHERE username = (%s)",
                           (escape_string(session['username'])))
            uID = cursor.fetchone()[0]

            # file path of images
            if not os.path.isdir(os.path.join(APP_ROOT, 'static/images/')):
                os.mkdir(os.path.join(APP_ROOT, 'static/images/'))

            APP_RELATED = 'static/images/' + session['username']
            target = os.path.join(APP_ROOT, APP_RELATED)

            # create a folder for the user if it does not exist
            if not os.path.isdir(target):
                os.mkdir(target)

            # check if file exists in the request
            if 'file' not in request.files:
                error = "file does not exist"
                return render_template("image-upload.html", title="upload images", error=error)

            # get the list for uploaded files
            for file in request.files.getlist("file"):
                # double check if the file exists
                if file == None or file.filename == '':
                    error = "file does not exist"
                    return render_template("image-upload.html", title="upload images", error=error)

                # give a pID to the new image
                cursor.execute("SELECT max(pID) FROM images")
                x = cursor.fetchone()
                if x[0] == None:
                    pID = 1;
                else:
                    pID = x[0] + 1

                # give a new image name accepted by database
                filename = str(file.filename).split('.')[-1]
                filename = escape_string(str(pID) + '.' + filename)

                # save the image file
                destination = "/".join([target, filename])
                file.save(destination)

                # insert the image info into the database
                cursor.execute("INSERT INTO images (pID, pName, users_userID) VALUES (%s, %s, %s)",
                               (int(pID), filename, int(uID)))

                # apply image transformation
                for i in range(3):
                    # give a tpID to the transformed image
                    cursor.execute("SELECT max(tpID) FROM trimages")
                    x = cursor.fetchone()
                    if x[0] == None:
                        tpID = 1;
                    else:
                        tpID = x[0] + 1

                    # give a file name to the transformed image
                    tfilename = escape_string("tr" + str(i) + "_" + filename)

                    # apply transformation
                    img = Image(filename=destination)
                    with img.clone() as tfile:
                        image_transfer(tfile, i)
                        # save the image file
                        tdestination = "/".join([target, tfilename])
                        tfile.save(filename=tdestination)
                        # insert the image info into the database
                        cursor.execute("INSERT INTO trimages (tpID, tpName, images_pID) VALUES (%s, %s, %s)",
                                   (int(tpID), tfilename, int(pID)))

            # database commit, cleanup and garbage collect
            cnx.commit()
            cursor.close()
            cnx.close()
            gc.collect()

            flash("upload successful")
            return redirect(url_for("gallery"))

        return render_template("image-upload.html", title="upload images")

    except Exception as e:
        teardown_db(e)
        return str(e)
