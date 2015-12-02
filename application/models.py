from application import db
from sqlalchemy import distinct

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


class Friends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    friend1 = db.Column(db.String(50), index=True, unique=False)
    friend2 = db.Column(db.String(50), index=True, unique=False)

    def __init__(self, friend1, friend2):
        self.friend1 = friend1
        self.friend2 = friend2

    def __repr__(self):
        return '<Friend %r>' % self.friend1

class movie_lists(db.Model):
    movieListID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), index=True, unique=False)
    movieID = db.Column(db.Integer, index=True, unique=False)

    def __init__(self, username, movieID):
        self.username = username
        self.movieID = movieID

    def __repr__(self):
        return '<ID %r>' % self.movieListID


class actor_movie_title(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), index=True, unique=False)
    Movie = db.Column(db.String(100), index=True, unique=False)

    def __init__(self, Name, Movie):
        self.Name = Name
        self.Movie = Movie

    def __repr__(self):
        return '<Name %r>' % self.Name

class actor_lists(db.Model):
    actorListID = db.Column(db.Integer, primary_key=True)
    actorName = db.Column(db.String(100), index=True, unique=False)
    username = db.Column(db.String(100), index=True, unique=False)

    def __init__(self, actorName, username):
        self.actorName = actorName
        self.username = username

    def __repr__(self):
        return '<Name %r>' % self.actorName


class Movie(db.Model):
    movieID = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True, unique=False)
    genre = db.Column(db.String(30), index=True, unique=False)
    releaseDate = db.Column(db.String(130), index=True, unique=False)

    def __init__(self, title, genre, releaseDate):
        self.title = title
        self.releaseDate = releaseDate
        self.genre = genre

    def __repr__(self):
        return '<Title %r>' % self.title


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notes = db.Column(db.String(128), index=True, unique=False)
    
    def __init__(self, notes):
        self.notes = notes

    def __repr__(self):
        return '<Data %r>' % self.notes