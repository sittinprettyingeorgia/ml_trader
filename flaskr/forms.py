from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class SignupForm(FlaskForm):
    # user sign up
    username = StringField(
        'Username',
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8, message='Password must be minimum of 8 characters.')
        ]
    )
    confirm = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')
        ]
    )
    submit = SubmitField(
        'Register'
    )


class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    submit = SubmitField('Login')
