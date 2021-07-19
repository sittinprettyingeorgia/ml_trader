from flask_login import UserMixin
import os
import joblib
import random
from flaskr import db
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib.pyplot as plt


# models that inherit from UserMixin get useful methods
# isactive, isauthentiicated, isanonymous, get_id, if user.is_active
class User(UserMixin, db.Model):
    # data model for users
    __tablename__ = 'Users'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    username = db.Column(
        db.String(20),
        index=False,
        unique=True,
        nullable=False
    )
    user_password = db.Column(
        db.String(200),
        primary_key=False,
        unique=False,
        nullable=False,
    )
    # create a table for a list of stocks associated with a user
    stocks = db.relationship('Stock', backref='User', lazy='joined')
    created_on = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=False
    )
    last_login = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=False
    )

    def set_password(self, user_password):
        # create hashed password
        self.user_password = generate_password_hash(user_password, method='sha256')

    def chk_password(self, user_password):
        return check_password_hash(self.user_password, user_password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Stock(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    ticker = db.Column(
        db.String(20),
        index=False,
        unique=True,
        nullable=False
    )
    is_fav = db.Column(
        db.Boolean,
        index=False,
        unique=False,
        nullable=False
    )
    # link each stock to a user
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)

    def __repr__(self):
        return '<Stock {}>'.format(self.ticker)


class ModelData:
    def __init__(self, ticker, model, test_predictions, test_y_vals):
        self.ticker = ticker
        self.model = model
        self.test_predictions = test_predictions
        self.test_y_vals = test_y_vals

    def get_model(self):
        my_file = f'{self.ticker}Model'
        current_path = os.path.abspath(os.getcwd())
        path = f'{current_path}\\flaskr\\home\\static\\src\\models\\{my_file}.pickle'
        return joblib.load(path)

    def get_graph(self):
        var1 = self.test_predictions
        var2 = self.test_y_vals
        plt.rcParams["figure.figsize"] = (16, 10)
        fig, ax = plt.subplots()

        x = []
        for index in range(var2.size):
            x.append(index)

        # graph the actual price data
        twin = ax.twinx()
        r = random.random()
        g = random.random()
        b = random.random()
        color = 'red'
        twin.plot(x, var2, color='red', label='Actual Close Price')
        twin.set_ylabel('Actual Close Price', fontsize=16)
        twin.yaxis.label.set_color(color)
        twin.tick_params(axis='y', labelcolor=color)

        # graph the predicted price data
        c, = ax.plot(x, var1, label='Predicted Close Price')
        ax.set_ylabel('Predicted Close Price', fontsize=16)
        ax.yaxis.label.set_color(c.get_color())
        ax.tick_params(axis='y', labelcolor=c.get_color())

        return fig
