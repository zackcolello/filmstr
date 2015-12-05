from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, validators, StringField


class RegistrationForm(Form):
    inputUsername = StringField('Username', [validators.Length(min=4, max=40)])
    inputPassword = PasswordField('Password', [validators.required()])
    inputFirstName = StringField('FirstName')
    inputLastName = StringField('FirstName')


class searchFriend(Form):
    searchName = StringField('searchName')
