from flask import Flask, render_template, redirect, url_for, flash, session
from functools import wraps

webapp = Flask(__name__)
webapp.secret_key='\x80\xa9s*\x12\xc7x\xa9d\x1f(\x03\xbeHJ:\x9f\xf0!\xb1a\xaa\x0f\xee'

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login_form'))

    return wrap

from app import main
from app import gallery
from app import login_signup