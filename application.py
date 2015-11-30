from flask import Flask, render_template, request, redirect, url_for, flash, session
from application import db
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from application.models import Data, Users
from application.forms import EnterDBInfo, RetrieveDBInfo, RegistrationForm
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

                return redirect(url_for('index'))

            else:
                error = "Invalid Credentials. Try again."

        return render_template('login.html', error=error)

    except Exception as e:
        return render_template("login.html", error=error)


@application.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

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
                return render_template('index.html')

            except Exception as e:
                db.session.rollback()

        return render_template('signup.html')

    except Exception as e:
        return str(e)

    # return render_template('signup.html')


@application.route('/movie', methods=['GET', 'POST'])
def movie():
    return render_template('movie.html')


@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    form1 = EnterDBInfo(request.form) 
    form2 = RetrieveDBInfo(request.form) 
    
    if request.method == 'POST' and form1.validate():
        data_entered = Data(notes=form1.dbNotes.data)
        try:     
            db.session.add(data_entered)
            db.session.commit()        
            db.session.close()
        except:
            db.session.rollback()
        return render_template('thanks.html', notes=form1.dbNotes.data)
        
    if request.method == 'POST' and form2.validate():
        try:   
            num_return = int(form2.numRetrieve.data)
            query_db = Data.query.order_by(Data.id.desc()).limit(num_return)
            for q in query_db:
                print(q.notes)
            db.session.close()
        except:
            db.session.rollback()
        return render_template('results.html', results=query_db, num_return=num_return)                
    
    return render_template('index.html', form1=form1, form2=form2)

if __name__ == '__main__':
    application.run(host='0.0.0.0')
