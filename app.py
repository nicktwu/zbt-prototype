#!/usr/bin/python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)


class Midnight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Date)
    zebe = db.Column(db.String(20))
    task = db.Column(db.String(80))
    notes = db.Column(db.String(300))

    def __init__(self, day, zebe, task, notes):
        self.day = day
        self.zebe = zebe
        self.task = task
        self.notes = notes


@app.route('/')
def hello_world():
    return 'Hello, you!'


if __name__ == '__main__':
    app.run()
