from flask import Blueprint, request, jsonify, abort
import os
from datetime import date as python_date, timedelta, datetime
from database import db
from models import Zebe, Midnight, MidnightAccount
from sqlalchemy import and_

midnights_page = Blueprint('midnights_page', __name__)

email = os.environ.get("SSL_CLIENT_S_DN_Email")

kerberos = ""
if email is not None:
    i = email.find("@")
    kerberos = email[:i]

midnight_permissions = {'nwu', 'silwal'}

CURRENT_SEMESTER = 'testing'

MIDNIGHT_REQUIREMENT = 0

ALL_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Accept, Content-Type',
}

CORS_HEADER = {
    'Access-Control-Allow-Origin': '*',
}


@midnights_page.route('/status')
def get_status():
    account = MidnightAccount.query.filter(MidnightAccount.zebe == kerberos).first()
    return jsonify({
        'kerberos': kerberos,
        'details': account if account is None else account.to_dict(),
        'error': False,
    }), 200, CORS_HEADER


@midnights_page.route('/create', methods=['POST', 'OPTIONS'])
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


@midnights_page.route('/create_multiple', methods=['POST', 'OPTIONS'])
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
    return jsonify({'midnights': [midnight.to_dict() for midnight in new_midnights]}), 201, ALL_HEADERS


@midnights_page.route('/weeklist/<int:year>/<int:month>/<int:day>')
def list_week_midnights(year, month, day):
    requested = python_date(year, month, day)
    week_start = week_of(requested)
    midnights = Midnight.query.filter(
        and_(Midnight.date >= week_start, Midnight.date <= week_start + timedelta(days=7))) \
        .all()
    responses = [midnight.to_dict() for midnight in midnights]
    response = {'midnights': responses}
    return jsonify(response), 200, CORS_HEADER


@midnights_page.route('/user/weeklist/<int:year>/<int:month>/<int:day>')
def list_user_week_status(year, month, day):
    requested = python_date(year, month, day)
    week_start = week_of(requested)
    midnights = Midnight.query.filter(
        and_(Midnight.date >= week_start, Midnight.date <= week_start + timedelta(days=7))) \
        .filter(Midnight.zebe == kerberos).all()
    account = MidnightAccount.query.filter(MidnightAccount.zebe == kerberos).first()
    return jsonify({'account': account, 'goal': MIDNIGHT_REQUIREMENT,
                    'midnights': [midnight.to_dict() for midnight in midnights]}), 200, CORS_HEADER


@midnights_page.route('/award/<int:id>/<int:points>', methods=['PUT', 'OPTIONS'])
def award_points(id, points):
    if request.method == "OPTIONS":
        return jsonify('ok'), 200, ALL_HEADERS
    if kerberos not in midnight_permissions:
        abort(401)
    midnight = Midnight.query.get_or_404(id)
    midnight.awarded = points
    db.session.commit()
    return jsonify({'midnight': midnight.to_dict()}), 200, ALL_HEADERS


@midnights_page.route('/authorized')
def is_authorized():
    return jsonify({'authorized': (kerberos in midnight_permissions)}), 200, CORS_HEADER


@midnights_page.route('/creatable_accounts')
def get_creatable_accounts():
    if kerberos not in midnight_permissions:
        return jsonify({'authorized': False}), 401, CORS_HEADER
    accounts = [account.zebe for account in MidnightAccount.query.filter(MidnightAccount.semester == CURRENT_SEMESTER).all()]
    zebes = [zebe.kerberos for zebe in Zebe.query.filter(Zebe.current).all()]
    possible = [zebe for zebe in zebes if zebe not in accounts]
    return jsonify({'authorized': True, 'possible': possible}), 200, CORS_HEADER


def valid_midnight(midnight):
    for field in {'date', 'zebe', 'task', 'potential'}:
        if field not in midnight:
            return False
    return True


def week_of(requested):
    return requested + timedelta(days=-(requested.isoweekday() % 7))