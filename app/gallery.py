from flask import render_template, redirect, url_for, request, g
from app import webapp

@webapp.route("/gallery")
def gallery():
    return render_template("thumbnail-gallery.html")