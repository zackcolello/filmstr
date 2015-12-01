from flask import Flask, render_template, request, redirect, url_for, flash, session
from application import db
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from application.models import Users, Friends, Actor_Movie_Title, movie_lists
from application.forms import EnterDBInfo, RetrieveDBInfo, RegistrationForm
from functools import wraps
from sqlalchemy.orm import Load
from wtforms import Form, TextField, validators


# Elastic Beanstalk initialization
application = Flask(__name__)
application.debug = True
# change this to your own value
application.secret_key = 'cC1YCIWOj9GgWspgNEo2'   
engine = create_engine('mysql+pymysql://zackcolello:Fmtvv22632@db.cqa9wktokxlq.us-west-2.rds.amazonaws.com:3306/db')


@application.route('/login/', methods=['GET', 'POST'])
def login():

    error = ''

    try:
        if request.method == "POST":  # User has entered username
            attempted_username = request.form['inputUsername']
            attempted_password = request.form['inputPassword']

            # Check if user exists

            metadata = MetaData(bind=engine)
            users = Table('users', metadata, autoload=True)

            r = users.select(users.c.email == attempted_username).execute().first()

            if r['pw'] != attempted_password:
                error = "Invalid Password. Try again."
                return render_template('signup.html', error=error)

            if r is not None:

                session['logged_in'] = True
                session['username'] = r['email']
                session['firstName'] = r['firstName']

                return redirect(url_for('home'))

            else:
                error = "Invalid Credentials. Try again."

        return render_template('login.html', error=error)

    except Exception as e:
        return render_template("login.html", error=error)


@application.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))



def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)

        else:
            flash("You need to log in first.")
            return redirect(url_for('login'))

@login_required
@application.route('/profile/<username>')
@application.route('/profile/')
def profile(username):

    metadata = MetaData(bind=engine)
    users = Table('users', metadata, autoload=True)

    user = db.session.query(users).filter(users.c.email == username).first()

    return render_template('profile.html', user=user)

@login_required
@application.route('/deletemovie/<movieID>', methods=['DELETE', 'POST', 'GET'])
def deletemovie(movieID):

    # Redirect to index if not logged in

    if 'logged_in' not in session:
        return redirect(url_for('index'))

    # Get friends list
    metadata = MetaData(bind=engine)
    #movie = Table('movie', metadata, autoload=True)
    #movie_lists = Table('movie_lists', metadata, autoload=True)

    #movie_lists.select(movie_lists.c.movieID == movieID).execute()

    movie_lists.query.filter_by(movieID=movieID).delete()
    db.session.commit()
    db.session.close()

    return redirect(url_for('mymovies'))

@login_required
@application.route('/deletefriend/<potentialfriend>', methods=['DELETE', 'POST', 'GET'])
def deletefriend(potentialfriend):
    # Get friends list
    metadata = MetaData(bind=engine)
    friends = Table('friends', metadata, autoload=True)
    users = Table('users', metadata, autoload=True)

    potentialfriend1 = users.select(users.c.email == potentialfriend).execute().first

    if potentialfriend is not None:

            #newfriendship = friends(friend1=session['username'], friend2=potentialfriend['email'])
            #newfriendship2 = friends(friend1=potentialfriend['email'], friend2=session['username'])

            myfriends = friends.select(friends.c.friend1 == session['username']).execute()
            myfriendsfriends = friends.select(friends.c.friend1 == potentialfriend).execute()

            newfriendship1 = None
            newfriendship2 = None

            for o in myfriends:
                if o[1] == potentialfriend:
                    newfriendship1 = o[2]
                    break

            for p in myfriendsfriends:
                if p[1] == session['username']:
                    newfriendship2 = p[2]
                    break

            try:

                Friends.query.filter_by(id=newfriendship2).delete()
                db.session.commit()
                db.session.close()

                Friends.query.filter_by(id=newfriendship1).delete()
                db.session.commit()
                db.session.close()

            except Exception as e:
                db.session.rollback()

    return redirect(url_for('myfriends'))



@login_required
@application.route('/addfriend/', methods=['POST'])
def addfriend():

    # Get friends list
    metadata = MetaData(bind=engine)
    friends = Table('friends', metadata, autoload=True)
    users = Table('users', metadata, autoload=True)

    if request.form.get('friendName', None) is not None:
        friendsearch = request.form.get('friendName', None)
        potentialfriend = users.select(users.c.email == friendsearch).execute().first()

        if potentialfriend is not None:

            newfriendship = Friends(friend1=session['username'], friend2=potentialfriend['email'])
            newfriendship2 = Friends(friend1=potentialfriend['email'], friend2=session['username'])

            try:
                db.session.add(newfriendship)
                db.session.add(newfriendship2)
                db.session.commit()
                db.session.close()

            except Exception as e:
                db.session.rollback()

    return redirect(url_for('myfriends'))


@login_required
@application.route('/', methods=['GET', 'POST'])
@application.route('/home', methods=['GET', 'POST'])
def home():

    # Get friends list
    metadata = MetaData(bind=engine)
    movies = Table('movie', metadata, autoload=True)

    # Redirect to index if not logged in

    if 'logged_in' not in session:
        return redirect(url_for('index'))

    # Get friends list
    metadata = MetaData(bind=engine)
    friends = Table('friends', metadata, autoload=True)
    users = Table('users', metadata, autoload=True)
    movie = Table('movie', metadata, autoload=True)
    movie_lists = Table('movie_lists', metadata, autoload=True)

    r = friends.select(friends.c.friend1 == session['username']).execute()

    friendArray = []
    for object in r:
        friendArray.append(object['friend2'])

    friends = []
    for object in friendArray:
        friends += db.session.query(users).filter(users.c.email == object)

    # Get movies list
    ml = movie_lists.select(movie_lists.c.username == session['username']).execute()

    movieIDArray = []
    for object in ml:
        movieIDArray.append(object['movieID'])

    moviesList = []
    for object in movieIDArray:
        moviesList += db.session.query(movies).filter(movies.c.movieID == object)


    if 'logged_in' not in session:
        return redirect(url_for('index'))

    return render_template('home.html', friends=friends, movies=moviesList)

@application.route('/signup', methods=['GET', 'POST'])
def signup():

    error = ''

    try:
        form = RegistrationForm(request.form)

        if request.method == "POST":
            username = form.inputUsername.data
            pw = form.inputPassword.data
            firstName = form.inputFirstName.data
            lastName = form.inputLastName.data

            # check if user already exists

            metadata = MetaData(bind=engine)
            users = Table('users', metadata, autoload=True)

            r = users.select(users.c.email == username).execute().first()

            if r is not None:
                error = "Username already taken. Try again."
                return render_template('signup.html', error=error)

            newuser = Users(pw=pw, firstName=firstName, lastName=lastName, email=username)

            try:
                db.session.add(newuser)
                db.session.commit()
                db.session.close()

                session['logged_in'] = True
                session['username'] = username
                session['firstName'] = firstName
                return render_template('home.html')

            except Exception as e:
                db.session.rollback()

        return render_template('signup.html')

    except Exception as e:
        return str(e)

    # return render_template('signup.html')


@application.route('/movie/', methods=['GET', 'POST'])
@application.route('/movie/<movieID>', methods=['GET', 'POST'])
def movie(movieID):

    # Get movie
    metadata = MetaData(bind=engine)
    movies = Table('movie', metadata, autoload=True)
    amt = Table('actor_movie_title', metadata, autoload=True)

    movie = movies.select(movies.c.movieID == movieID).execute().first()
    title = movie['title']

    actors = amt.select(amt.c.Movie == title).execute()


    return render_template('movie.html', movie=movie, actors=actors)


@application.route('/mymovies', methods=['GET', 'POST'])
def mymovies():

    # Get movies list
    metadata = MetaData(bind=engine)
    movies = Table('movie', metadata, autoload=True)

    # Redirect to index if not logged in

    if 'logged_in' not in session:
        return redirect(url_for('index'))

    movie = Table('movie', metadata, autoload=True)
    movie_lists = Table('movie_lists', metadata, autoload=True)

    # Get movies list
    ml = movie_lists.select(movie_lists.c.username == session['username']).execute()

    movieIDArray = []
    for object in ml:
        movieIDArray.append(object['movieID'])

    moviesList = []
    for object in movieIDArray:
        moviesList += db.session.query(movies).filter(movies.c.movieID == object)

    if 'logged_in' not in session:
        return redirect(url_for('index'))

    return render_template('mymovies.html', movies=moviesList)


@application.route('/myfriends', methods=['GET', 'POST'])
def myfriends():

    # Get friends list

    # Redirect to index if not logged in

    if 'logged_in' not in session:
        return redirect(url_for('index'))

    # Get friends list
    metadata = MetaData(bind=engine)
    friends = Table('friends', metadata, autoload=True)
    users = Table('users', metadata, autoload=True)

    r = friends.select(friends.c.friend1 == session['username']).execute()

    friendArray = []
    for object in r:
        friendArray.append(object['friend2'])

    friends = []
    for object in friendArray:
        friends += db.session.query(users).filter(users.c.email == object)

    return render_template('myfriends.html', friends=friends)


@application.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    application.run(host='0.0.0.0')
