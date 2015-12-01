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


class Actor_Movie_Title(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=False)
    movie = db.Column(db.String(100), index=True, unique=False)

    def __init__(self, name, movie):
        self.name = name
        self.movie = movie

    def __repr__(self):
        return '<Name %r>' % self.name


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