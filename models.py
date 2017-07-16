from database import db


class Zebe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kerberos = db.Column(db.String(30))
    name = db.Column(db.String(100))
    current = db.Column(db.Boolean)

    def __init__(self, username, name, current):
        self.kerberos = username
        self.name = name
        self.current = current

    def to_dict(self):
        return {
            'id': self.id,
            'kerberos': self.kerberos,
            'name': self.name,
            'current': self.current,
        }


class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    start = db.Column(db.Date)
    end = db.Column(db.Date)

    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'start': str(self.start),
            'end': str(self.end),
        }


class Midnight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    zebe = db.Column(db.String(30))
    task = db.Column(db.String(80))
    note = db.Column(db.String(300))
    feedback = db.Column(db.String(300))
    potential = db.Column(db.Float)
    awarded = db.Column(db.Float)
    reviewed = db.Column(db.Boolean)

    def __init__(self, date, zebe, task, note, feedback, potential, awarded, reviewed):
        self.date = date
        self.zebe = zebe
        self.task = task
        self.note = note
        self.feedback = feedback
        self.potential = potential
        self.awarded = awarded
        self.reviewed = reviewed

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
            'reviewed': self.reviewed
        }


class MidnightAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.String(50))
    zebe = db.Column(db.String(30))
    balance = db.Column(db.Float)
    requirement = db.Column(db.Float)

    def __init__(self, semester, zebe, balance, requirement):
        self.semester = semester
        self.zebe = zebe
        self.balance = balance
        self.requirement = requirement

    def to_dict(self):
        return {
            'id': self.id,
            'semester': self.semester,
            'zebe': self.zebe,
            'balance': self.balance,
            'required': self.requirement,
        }


class MidnightTypeDefault(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    value = db.Column(db.Float)
    description = db.Column(db.String(500))

    def __init__(self, name, value, description):
        self.name = name
        self.value = value
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value,
            'description': self.description,
        }


class MidnightTrade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    midnight = db.Column(db.Integer, db.ForeignKey('midnight.id'))
    zebe = db.Column(db.Integer, db.ForeignKey('midnight_account.id'))
    offered = db.Column(db.Float)
    completed = db.Column(db.Boolean)
    taker = db.Column(db.String(30))

    def __init__(self, midnight, zebe, offered, completed, taker):
        self.midnight = midnight
        self.zebe = zebe
        self.offered = offered
        self.completed = completed
        self.taker = taker

    def to_dict(self):
        return {
            'id': self.id,
            'midnight': self.midnight,
            'zebe': self.zebe,
            'offered': self.offered,
            'completed': self.completed,
            'taker': self.taker,
        }


class WorkweekTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500))
    hours = db.Column(db.Float)
    taker = db.Column(db.String(30))
    completed = db.Column(db.Boolean)

    def __init__(self, description, hours, taken, completed):
        self.description = description
        self.hours = hours
        self.taker = taken
        self.completed = completed

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'hours': self.hours,
            'taker': self.taker,
            'completed': self.completed,
        }
