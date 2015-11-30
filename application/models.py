from application import db


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pw = db.Column(db.String, index=True)
    firstName = db.Column(db.String, index=True)
    lastName = db.Column(db.String, index=True)
    email = db.Column(db.String, index=True)

    def __init__(self, email, pw, firstName, lastName):
        self.email = email
        self.pw = pw
        self.firstName = firstName
        self.lastName = lastName

    def __repr__(self):
        return '<Email %r>' % self.email


class Movie(db.Model):
    movieID = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True, unique=False)

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return '<Data %r>' % self.notes


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notes = db.Column(db.String(128), index=True, unique=False)
    
    def __init__(self, notes):
        self.notes = notes

    def __repr__(self):
        return '<Data %r>' % self.notes