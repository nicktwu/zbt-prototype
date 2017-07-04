#!/usr/bin/python
from flask import Flask
from database import db
import os

app = Flask(__name__)
app.config.from_pyfile('config.py')
db.init_app(app)

from midnights import midnights_page
app.register_blueprint(midnights_page, url_prefix="/midnights")
app.app_context().push()

email = os.environ.get("SSL_CLIENT_S_DN_Email")
kerberos = ""

if email is not None:
    i = email.find("@")
    kerberos = email[:i]


@app.route('/')
def hello_world():
    return 'Hello, ' + kerberos + '!'


if __name__ == '__main__':
    app.run()
