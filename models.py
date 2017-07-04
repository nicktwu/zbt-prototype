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
    requirement = db.Column(db.Integer)

    def __init__(self, semester, start, end, zebe, balance, requirement):
        self.semester = semester
        self.start = start
        self.end = end
        self.zebe = zebe
        self.balance = balance
        self.requirement = requirement

    def to_dict(self):
        return {
            'id': self.id,
            'semester': self.semester,
            'start': str(self.start),
            'end': str(self.end),
            'zebe': self.zebe,
            'balance': self.balance,
            'required': self.requirement,
        }