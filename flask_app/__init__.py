import os
from flask import Flask, session 
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "Python project shhhhhh")
