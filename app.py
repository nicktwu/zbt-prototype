#!/usr/bin/python
from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date as python_date, timedelta, datetime
import os
from sqlalchemy import and_

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
app.app_context().push()

email = os.environ.get("SSL_CLIENT_S_DN_Email")
kerberos = ""

if email is not None:
    i = email.find("@")
    kerberos = email[:i]

midnight_permissions = {'nwu', 'silwal'}

CURRENT_SEMESTER = 'testing'

ALL_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Accept, Content-Type',
}

CORS_HEADER = {
    'Access-Control-Allow-Origin': '*',
}


class Midnight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    zebe = db.Column(db.String(30))
    task = db.Column(db.String(80))
    note = db.Column(db.String(300))
    feedback = db.Column(db.String(300))
    potential = db.Column(db.Integer)
    awarded = db.Column(db.Integer)

    def __init__(self, date, zebe, task, note, feedback, potential, awarded):
        self.date = date
        self.zebe = zebe
        self.task = task
        self.note = note
        self.feedback = feedback
        self.potential = potential
        self.awarded = awarded

    def to_dict(self):
        return {
            'id': self.id,
            'date': str(self.date),
            'zebe': self.zebe,
            'task': self.task,
            'note': self.note,
            'feedback': self.feedback,
            'potential': self.potential,
            'awarded': self.awarded,
        }


class MidnightAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.String(50))
    start = db.Column(db.Date)
    end = db.Column(db.Date)
    zebe = db.Column(db.String(30))
    balance = db.Column(db.Integer)

    def __init__(self, semester, start, end, zebe, balance):
        self.semester = semester
        self.start = start
        self.end = end
        self.zebe = zebe
        self.balance = balance

    def to_dict(self):
        return {
            'id': self.id,
            'semester': self.semester,
            'start': self.start,
            'end': self.end,
            'zebe': self.zebe,
            'balance': self.balance,
        }


@app.route('/')
def hello_world():
    return 'Hello, ' + kerberos + '!'


@app.route('/midnights/status')
def get_status():
    account = MidnightAccount.query.filter(MidnightAccount.zebe == kerberos).first()
    return jsonify({
        'kerberos': kerberos,
        'details': account if account is None else account.to_dict(),
        'error': False,
    }), 200, CORS_HEADER


@app.route('/midnights/create', methods=['POST', 'OPTIONS'])
def create_midnight():
    if request.method == "OPTIONS":
        return jsonify('ok'), 200, ALL_HEADERS
    if kerberos not in midnight_permissions:
        abort(401)
    if not request.json:
        abort(400)
    if not valid_midnight(request.json):
        abort(400)
    midnight = Midnight(
        datetime.fromtimestamp(request.json['date'] / 1000).date(),
        request.json['zebe'],
        request.json['task'],
        request.json.get('note', ''),
        request.json.get('feedback', ''),
        request.json['potential'],
        request.json.get('awarded', 0),
    )
    db.session.add(midnight)
    db.session.commit()
    return jsonify(midnight.to_dict()), 201, ALL_HEADERS


@app.route('/midnights/create_multiple', methods=['POST', 'OPTIONS'])
def create_midnights():
    if request.method == "OPTIONS":
        return jsonify('ok'), 200, ALL_HEADERS
    if kerberos not in midnight_permissions:
        abort(401)
    if not request.json:
        abort(400)
    if 'midnights' not in request.json:
        abort(400)
    new_midnights = []
    for new_midnight in request.json.midnights:
        if not valid_midnight(new_midnight):
            abort(400)
        midnight = Midnight(
            datetime.fromtimestamp(new_midnight['date'] / 1000).date(),
            new_midnight['zebe'],
            new_midnight['task'],
            new_midnight.get('note', ''),
            new_midnight.get('feedback', ''),
            new_midnight['potential'],
            new_midnight.get('awarded', 0),
        )
        new_midnights.append(midnight)
        db.session.add(midnight)
    db.session.commit()
    return jsonify({'midnights':[midnight.to_dict() for midnight in new_midnights]}), 201, ALL_HEADERS


@app.route('/midnights/weeklist/<int:year>/<int:month>/<int:day>')
def list_week_midnights(year, month, day):
    requested = python_date(year, month, day)
    week_start = week_of(requested)
    midnights = Midnight.query.filter(
        and_(Midnight.date >= week_start, Midnight.date <= week_start + timedelta(days=7))) \
        .all()
    responses = [midnight.to_dict() for midnight in midnights]
    response = {'midnights': responses}
    return jsonify(response), 200, CORS_HEADER


@app.route('/midnights/daylist/<int:year>/<int:month>/<int:day>')
def list_day_midnights(year, month, day):
    requested = python_date(year, month, day)
    midnights = Midnight.query.filter(Midnight.date == requested).all()
    return jsonify({'midnights':[midnight.to_dict() for midnight in midnights]}), 200, CORS_HEADER


@app.route('/midnights/user/weeklist/<int:year>/<int:month>/<int:day>')
def list_user_week_midnights(year, month, day):
    requested = python_date(year, month, day)
    week_start = week_of(requested)
    midnights = Midnight.query.filter(
        and_(Midnight.date >= week_start, Midnight.date <= week_start + timedelta(days=7))) \
        .filter(Midnight.zebe == kerberos).all()
    return jsonify({'midnights':[midnight.to_dict() for midnight in midnights]}), 200, CORS_HEADER


@app.route('/midnights/user/daylist/<int:year>/<int:month>/<int:day>')
def list_user_day_midnights(year, month, day):
    requested = python_date(year, month, day)
    midnights = Midnight.query.filter(Midnight.date == requested).filter(Midnight.zebe == kerberos).all()
    return jsonify({'midnights':[midnight.to_dict() for midnight in midnights]}), 200, CORS_HEADER


@app.route('/midnights/award/<int:id>/<int:points>', methods=['PUT', 'OPTIONS'])
def award_points(id, points):
    if request.method == "OPTIONS":
        return jsonify('ok'), 200, ALL_HEADERS
    if kerberos not in midnight_permissions:
        abort(401)
    midnight = Midnight.query.get_or_404(id)
    midnight.awarded = points
    db.session.commit()
    return jsonify({'midnight': midnight.to_dict()}), 200, ALL_HEADERS

@app.route('/midnights/authorized')
def is_authorized():
    return jsonify({'authorized': (kerberos in midnight_permissions)}), 200, CORS_HEADER


def week_of(requested):
    return requested + timedelta(days=-(requested.isoweekday() % 7))


def valid_midnight(midnight):
    for field in {'date', 'zebe', 'task', 'potential'}:
        if field not in midnight:
            return False
    return True


if __name__ == '__main__':
    app.run()
