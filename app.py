#!/usr/bin/python
from flask import Flask
from database import db
import os
from midnights import midnights_page
from trades import trading_page
from workweek import workweek_page

app = Flask(__name__)
app.config.from_pyfile('config.py')
db.init_app(app)
app.register_blueprint(midnights_page, url_prefix="/midnights")
app.register_blueprint(trading_page, url_prefix="/trading")
app.register_blueprint(workweek_page, url_prefix="/workweek")
app.app_context().push()
app.debug = True
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
