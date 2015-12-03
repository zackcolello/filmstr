from flask import Flask, render_template, request, redirect, url_for, flash, session
from application import db
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from application.models import Users, Friends, actor_movie_title, movie_lists, Movie, actor_lists, actors
from application.forms import EnterDBInfo, RetrieveDBInfo, RegistrationForm
from functools import wraps


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
                return render_template('login.html', error=error)

            if r is not None:

                session['logged_in'] = True
                session['username'] = r['email']
                session['firstName'] = r['firstName']

                # Get movies list
                metadata = MetaData(bind=engine)
                movies = Table('movie', metadata, autoload=True)
                movie_lists = Table('movie_lists', metadata, autoload=True)

                # Get movies list
                ml = movie_lists.select(movie_lists.c.username == session['username']).execute()

                movieIDArray = []
                for object in ml:
                    movieIDArray.append(object['movieID'])

                moviesList = []
                for object in movieIDArray:
                    moviesList += db.session.query(movies).filter(movies.c.movieID == object)

                return render_template('mymovies.html', movies=moviesList, loginsuccess="true")

            else:
                error = "Invalid Credentials. Try again."

        return render_template('login.html', error=error)

    except Exception as e:
        error='Invalid credentials. Try again.'
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
    moviesID = movie_lists.query.with_entities(movie_lists.movieID).filter(movie_lists.username.like(username)).all()
    actors = actor_lists.query.with_entities(actor_lists.actorName).filter(actor_lists.username.like(username)).all()

    myMovieArray = []

    for m in moviesID:
        myMovieArray.append(m[0])

    returnMov = Movie.query.filter(Movie.movieID.in_(myMovieArray)).all()


    return render_template('profile.html', user=user, movies=returnMov, actors=actors)


@application.route('/viewSimilarMovies/<username>', methods=['POST', 'GET'])
def viewSimilarMovies(username):

    movies = movie_lists.query.with_entities(movie_lists.movieID).filter(movie_lists.username.like(username)).all()
    myMovies = movie_lists.query.with_entities(movie_lists.movieID).filter(movie_lists.username.like(session['username'])).all()

    movieIntersect = set(movies).intersection(myMovies)

    myMovieArray = []

    for m in movieIntersect:
        myMovieArray.append(m[0])

    returnMov = Movie.query.filter(Movie.movieID.in_(myMovieArray)).all()

    return render_template('viewsimilarmovies.html', username=username, movies=returnMov)


@application.route('/viewSimilarActors/<username>', methods=['POST', 'GET'])
def viewSimilarActors(username):

    actors = actor_lists.query.with_entities(actor_lists.actorName).filter(actor_lists.username.like(username)).all()
    myActors = actor_lists.query.with_entities(actor_lists.actorName).filter(movie_lists.username.like(session['username'])).all()

    actorIntersect = set(actors).intersection(myActors)

    return render_template('viewsimilaractors.html', username=username, movies=actorIntersect)

@application.route('/searchactor/', methods=['POST', 'GET'])
def searchactor():

    actorlist = ''

    if request.form.get('actorSearch', None) is not None:
        queryName = request.form.get('actorSearch', None)

        actorlist = actors.query.filter(actors.name.like('%' + queryName + '%')).limit(30).all()

    return render_template('searchactor.html', actors=actorlist)


@application.route('/searchmovie/', methods=['POST', 'GET'])
def searchmovie():

    movies = None

    if request.form.get('movieSearch', None) is not None:
        queryTitle = request.form.get('movieSearch', None)

        metadata = MetaData(bind=engine)
        movies = Movie.query.filter(Movie.title.like('%' + queryTitle + '%')).all()


    return render_template('searchmovie.html', movies=movies)



@login_required
@application.route('/deleteactor/<actorName>', methods=['DELETE', 'POST', 'GET'])
def deleteactor(actorName):
     # Redirect to index if not logged in

    if 'logged_in' not in session:
        return redirect(url_for('index'))

    actor_lists.query.filter_by(actorName=actorName).delete()
    db.session.commit()
    db.session.close()

    #  Get actors list
    actors = actor_lists.query.filter(actor_lists.username.like(session['username'])).all()

    return render_template('myactors.html', actors=actors, deletesuccess="true")


@login_required
@application.route('/deletemovie/<movieID>', methods=['DELETE', 'POST', 'GET'])
def deletemovie(movieID):

    # Redirect to index if not logged in

    if 'logged_in' not in session:
        return redirect(url_for('index'))

    movie_lists.query.filter_by(movieID=movieID).delete()
    db.session.commit()
    db.session.close()

        # Get movies list
    metadata = MetaData(bind=engine)
    movies = Table('movie', metadata, autoload=True)
    movielist = Table('movie_lists', metadata, autoload=True)

    # Get movies list
    ml = movielist.select(movielist.c.username == session['username']).execute()

    movieIDArray = []
    for object in ml:
        movieIDArray.append(object['movieID'])

    moviesList = []
    for object in movieIDArray:
        moviesList += db.session.query(movies).filter(movies.c.movieID == object)

    return render_template('mymovies.html', movies=moviesList, deletesuccess="true")

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
@application.route('/addactor/<actorName>', methods=['GET', 'POST'])
def addactor(actorName):
    metadata = MetaData(bind=engine)
    al = Table('actor_lists', metadata, autoload=True)

    newActorListItem = actor_lists(username=session['username'], actorName=actorName)

    # Check if actor exists
    potentialactor = al.select(al.c.username == session['username']).execute()

    for o in potentialactor:
        if o['actorName'] == actorName:
            return redirect(url_for('myactors'))

    db.session.add(newActorListItem)
    db.session.commit()
    db.session.close()

        #  Get actors list
    actors = actor_lists.query.filter(actor_lists.username.like(session['username'])).all()

    return render_template('myactors.html', actors=actors, addsuccess="true")

@login_required
@application.route('/addmovie/<movieID>', methods=['GET', 'POST'])
def addmovie(movieID):

    metadata = MetaData(bind=engine)
    ml = Table('movie_lists', metadata, autoload=True)
    # newMovie = movie_lists(username=session['username'], movieID=movieID)

    movieToBeAdded = Movie.query.filter(Movie.movieID.like(movieID)).first()

    newMovieListItem = movie_lists(username=session['username'], movieID=movieToBeAdded.movieID)

    # Check if movie exists
    potentialmovie = ml.select(ml.c.username == session['username']).execute()

    for o in potentialmovie:
        if o['movieID'] == movieID:
            return redirect(url_for('mymovies'))

    db.session.add(newMovieListItem)
    db.session.commit()
    db.session.close()

    # Get movies list
    metadata = MetaData(bind=engine)
    movies = Table('movie', metadata, autoload=True)
    movielist = Table('movie_lists', metadata, autoload=True)

    # Get movies list
    ml = movielist.select(movielist.c.username == session['username']).execute()

    movieIDArray = []
    for object in ml:
        movieIDArray.append(object['movieID'])

    moviesList = []
    for object in movieIDArray:
        moviesList += db.session.query(movies).filter(movies.c.movieID == object)

    return render_template('mymovies.html', movies=moviesList, addsuccess="true")


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
                return render_template('mymovies.html', loginsuccess="true")

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

    movie1 = Movie.query.with_entities(Movie.title, Movie.genre, Movie.movieID).filter(Movie.movieID.like(movieID)).first()
    Str = movie1[0]
    actors = actor_movie_title.query.filter(actor_movie_title.Movie.like(Str)).limit(30).all()
    return render_template('movie.html', movie=movie1, actors=actors)

@login_required
@application.route('/myactors', methods=['GET', 'POST'])
def myactors():

    # Redirect to index if not logged in
    if 'logged_in' not in session:
        return redirect(url_for('index'))

    #  Get actors list
    actors = actor_lists.query.filter(actor_lists.username.like(session['username'])).all()

    return render_template('myactors.html', actors=actors)


@application.route('/mymovies', methods=['GET', 'POST'])
@application.route('/', methods=['GET', 'POST'])
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
