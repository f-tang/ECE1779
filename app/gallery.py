from flask import render_template, redirect, url_for, request, g
from app import webapp, login_required


@webapp.route("/gallery")
@login_required
def gallery():
    return render_template("thumbnail-gallery.html")