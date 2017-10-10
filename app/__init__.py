from flask import Flask

webapp = Flask(__name__)

from app import main
from app import gallery
from app import login_signup