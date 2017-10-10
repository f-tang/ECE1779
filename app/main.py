from flask import render_template, redirect, url_for, request, g
from app import webapp

@webapp.route('/',methods=['GET'])
@webapp.route('/index',methods=['GET'])
def main():
    return render_template("index.html")