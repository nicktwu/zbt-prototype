from flask import Blueprint, request, jsonify, abort
import os
from datetime import date as python_date, timedelta, datetime
from database import db
from models import Zebe, Midnight, MidnightAccount, MidnightTypeDefault
from sqlalchemy import and_

midnights_page = Blueprint('midnights_page', __name__)

email = os.environ.get("SSL_CLIENT_S_DN_Email")

kerberos = ""
if email is not None:
    i = email.find("@")
    kerberos = email[:i]

midnight_permissions = {'nwu', 'silwal'}

CURRENT_SEMESTER = 'testing'
PREVIOUS_SEMESTER = 'old-testing'

MIDNIGHT_REQUIREMENT = 0

ALL_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS',
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


@midnights_page.route('/accounts')
def list_accounts():
    accounts = MidnightAccount.query.filter(MidnightAccount.semester == CURRENT_SEMESTER).all()
    return jsonify({'accounts': [account.to_dict() for account in accounts]}), 200, CORS_HEADER


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
    account = MidnightAccount.query.filter(MidnightAccount.zebe == kerberos).filter(
        MidnightAccount.semester == CURRENT_SEMESTER).first()
    reviewed = Midnight.query.filter(Midnight.reviewed).filter(
        Midnight.date >= python_date.today() + timedelta(days=-7)) \
        .filter(Midnight.zebe == kerberos)
    return jsonify({'account': account.to_dict(), 'goal': MIDNIGHT_REQUIREMENT,
                    'midnights': [midnight.to_dict() for midnight in midnights],
                    'reviewed': [midnight.to_dict() for midnight in reviewed]}), 200, CORS_HEADER


@midnights_page.route('/options')
def list_options():
    zebes = [zebe.to_dict() for zebe in Zebe.query.filter(Zebe.current).all()]
    defaults = [default.to_dict() for default in MidnightTypeDefault.query.all()]
    return jsonify(
        {'zebes': zebes, 'defaults': defaults, 'authorized': (kerberos in midnight_permissions)}), 200, CORS_HEADER


@midnights_page.route('/tasks', methods=['GET', 'PUT', 'OPTIONS'])
def list_tasks():
    if kerberos not in midnight_permissions:
        abort(401)
    if request.method == "OPTIONS":
        return jsonify({'status': 'ok'}), 200, ALL_HEADERS
    if request.method == "PUT":
        return jsonify({'status': 'ok'}), 200, ALL_HEADERS
    if request.method == "GET":
        return jsonify(
            {'tasks': [task.to_dict() for task in MidnightTypeDefault.query.all()]}
        ), 200, CORS_HEADER


@midnights_page.route('/create_type', methods=['POST','OPTIONS'])
def create_type():
    if kerberos not in midnight_permissions:
        abort(401)
    if request.method == "OPTIONS":
        return jsonify({'status': 'ok'}), 200, ALL_HEADERS
    if not request.json:
        abort(400)
    if 'value' not in request.json or 'name' not in request.json:
        abort(400)
    q = MidnightTypeDefault.query.filter(MidnightTypeDefault.name == request.json['name']).count()
    if q > 0:
        return jsonify({'error':'Name already exists'}), 200, ALL_HEADERS
    default = MidnightTypeDefault(request.json['name'], request.json['value'], request.json.get('description',''))
    db.session.add(default)
    db.session.commit()
    return jsonify({'type': default.to_dict()}), 201, ALL_HEADERS


@midnights_page.route('/update_types', methods=['PUT', 'OPTIONS'])
def update_types():
    if kerberos not in midnight_permissions:
        abort(401)
    if request.method == "OPTIONS":
        return jsonify({'status':'ok'}), 200, ALL_HEADERS
    if not request.json:
        abort(400)
    if 'types' not in request.json:
        abort(400)
    for t in request.json['types']:
        task = MidnightTypeDefault.query.get_or_404(t.get('id'))
        task.value = t.get('value')
        task.description = t.get('description')
    db.session.commit()
    return jsonify({'status': 'ok'}), 200, ALL_HEADERS


@midnights_page.route('/authorized')
def is_authorized():
    return jsonify({'authorized': (kerberos in midnight_permissions)}), 200, CORS_HEADER


@midnights_page.route('/create', methods=['POST', 'OPTIONS'])
def create_midnight():
    if request.method == "OPTIONS":
        return jsonify({'status': 'ok'}), 200, ALL_HEADERS
    if kerberos not in midnight_permissions:
        abort(401)
    if not request.json:
        abort(400)
    if not valid_midnight(request.json):
        abort(400)
    midnight = Midnight(
        datetime.strptime(request.json['date'], '%Y-%m-%dT%H:%M:%S.%fZ'),
        request.json['zebe'],
        request.json['task'],
        request.json.get('note', ''),
        request.json.get('feedback', ''),
        request.json['potential'],
        request.json.get('awarded', 0),
        request.json.get('reviewed', False),
    )
    db.session.add(midnight)
    db.session.commit()
    return jsonify(midnight.to_dict()), 201, ALL_HEADERS


@midnights_page.route('/create_multiple', methods=['POST', 'OPTIONS'])
def create_midnights():
    if request.method == "OPTIONS":
        return jsonify({'status': 'ok'}), 200, ALL_HEADERS
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
            new_midnight.get('reviewed', False),
        )
        new_midnights.append(midnight)
        db.session.add(midnight)
    db.session.commit()
    return jsonify({'midnights': [midnight.to_dict() for midnight in new_midnights]}), 201, ALL_HEADERS


@midnights_page.route('/creatable_accounts')
def get_creatable_accounts():
    if kerberos not in midnight_permissions:
        return jsonify({'authorized': False}), 401, CORS_HEADER
    accounts = [account.zebe for account in
                MidnightAccount.query.filter(MidnightAccount.semester == CURRENT_SEMESTER).all()]
    zebes = [zebe.kerberos for zebe in Zebe.query.filter(Zebe.current).all()]
    possible = [zebe for zebe in zebes if zebe not in accounts]
    return jsonify({'authorized': True, 'possible': possible}), 200, CORS_HEADER


@midnights_page.route('/create_accounts', methods=['POST', 'OPTIONS'])
def create_accounts():
    if request.method == "OPTIONS":
        return jsonify({'status': 'ok'}), 200, ALL_HEADERS
    if kerberos not in midnight_permissions:
        abort(401)
    if not request.json:
        abort(400)
    if 'accounts' not in request.json:
        abort(400)
    new_accounts = []
    for new_account in request.json['accounts']:
        old_account = MidnightAccount.query.filter(MidnightAccount.semester == PREVIOUS_SEMESTER) \
            .filter(MidnightAccount.zebe == new_account).first()
        check = MidnightAccount.query \
            .filter(MidnightAccount.semester == CURRENT_SEMESTER) \
            .filter(MidnightAccount.zebe == new_account).count()
        bal = 0
        if old_account is not None:
            bal = old_account.balance - old_account.requirement
        if check < 1:
            account = MidnightAccount(
                CURRENT_SEMESTER,
                new_account,
                bal,
                -1,
            )
            new_accounts.append(account)
            db.session.add(account)
    db.session.commit()
    return jsonify({'midnights': [account.to_dict() for account in new_accounts]}), 201, ALL_HEADERS


@midnights_page.route('/award/<int:id>', methods=['PUT', 'OPTIONS'])
def award_points(id):
    if request.method == "OPTIONS":
        return jsonify({'status': 'ok'}), 200, ALL_HEADERS
    if kerberos not in midnight_permissions:
        abort(401)
    if not request.json or 'points' not in request.json:
        abort(400)
    midnight = Midnight.query.get_or_404(id)
    midnight.awarded = request.json['points']
    midnight.feedback = request.json.get('note', '')
    midnight.reviewed = True
    zebe = MidnightAccount.query.filter(MidnightAccount.semester == CURRENT_SEMESTER).filter(
        MidnightAccount.zebe == midnight.zebe).one()
    zebe.balance = zebe.balance + request.json['points']
    db.session.commit()
    return jsonify({'midnight': midnight.to_dict()}), 200, ALL_HEADERS


@midnights_page.route('/review')
def get_midnights_to_review():
    if kerberos not in midnight_permissions:
        abort(401)
    present = python_date.today()
    midnights = Midnight.query.filter(Midnight.reviewed.is_(False)).filter(present >= Midnight.date).all()
    return jsonify({'midnights': [midnight.to_dict() for midnight in midnights]}), 200, CORS_HEADER


def valid_midnight(midnight):
    for field in {'date', 'zebe', 'task', 'potential'}:
        if field not in midnight:
            return False
    return True


def week_of(requested):
    return requested + timedelta(days=-(requested.isoweekday() % 7))
