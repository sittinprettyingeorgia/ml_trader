from flask import Blueprint, redirect, render_template, url_for, send_file, make_response, Response, session
from flask_login import current_user, login_required, logout_user
from flask import jsonify, request
from ..models import db, Stock
from . import graphs
from .. import ml_builder as ml
import os
import joblib
from .. import models

my_dict = {
    "Close": 1,
    "Open": 2,
    "High": 3,
    "Low": 4,
    "Volume": 5
}

# Blueprint Configuration
home_bp = Blueprint(
    'home_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@home_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    # render homepage
    stocks = Stock.query.filter_by(user_id=current_user.get_id()).limit(5).all()
    if 'currId' in session:
        curr = session['currId'].upper()

    else:
        curr = ""
    return render_template(
        'dashboard.jinja2',
        title='Smart Trader',
        description='user homepage',
        template='dashboard',
        current_user=current_user,
        stocks=stocks,
        currTicker=curr,
        body=f'Welcome back to Smart Trader {current_user.username}'
    )


@home_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_bp.login'))


@home_bp.route('/graph.png', methods=['GET', 'POST'])
@login_required
def graph():
    if request.method == 'POST':
        data = request.get_json()
        name = data['ticker']
        plot = data['plotType']
        data_vars = data['variables'][:2]
        variables = ""
        for variable in data_vars:
            variables += variable

        session['currId'] = name
        session['currPlot'] = plot
        session['currVariables'] = variables
        stock = Stock.query.filter_by(ticker=name).first()
        ticker = ml.get_ticker(stock.ticker, '1d')

        if f'{name}{plot}{variables}DataPng' not in session:
            if not data_vars:
                data_vars = None

            if stock is None:
                message = 'Please make sure to add a stock to the database with the add button before generating ' \
                          'graphs with the graph data button.'
            png_graph = graphs.get_graph(ticker, plot, data_vars)
            my_file = f'{name}{plot}{variables}DataPng'
            session[my_file] = my_file
            # current_path = os.path.abspath(os.getcwd())
            abs_path = os.path.abspath('flaskr/')
            path = f'{abs_path}home\\static\\dist\\images\\{my_file}.png'
            png_graph.savefig(path)

        message = []

        if data_vars:
            for data in data_vars:

                session[f'{name}{data}Mode'] = float(ticker[data].mode().min())
                session[f'{name}{data}Median'] = float(ticker[data].median().min())
                session[f'{name}{data}Mean'] = float(ticker[data].mean().min())

                message.append(my_dict[data])
                message.append(session[f'{name}{data}Mode'])
                message.append(session[f'{name}{data}Median'])
                message.append(session[f'{name}{data}Mean'])
        else:
            data = 'Close'
            session[f'{name}{data}Mode'] = float(ticker['Close'].mode().min())
            session[f'{name}{data}Median'] = float(ticker[data].median().min())
            session[f'{name}{data}Mean'] = float(ticker[data].mean().min())

            message.append(my_dict[data])
            message.append(session[f'{name}{data}Mode'])
            message.append(session[f'{name}{data}Median'])
            message.append(session[f'{name}{data}Mean'])

        message = jsonify(message)
        return message, 200

    else:
        name = ""
        plot = ""
        variables = ""

        if 'currId' in session:
            name = session['currId']
            plot = session['currPlot']
            variables = session['currVariables']

        if f'{name}{plot}{variables}DataPng' in session:
            abs_path = os.path.abspath('flaskr/')
            my_file = f'{name}{plot}{variables}DataPng'
            path = f'{abs_path}home\\static\\dist\\images\\{my_file}.png'
            return send_file(path, mimetype='image/png')

        else:
            stock = Stock.query.filter_by(user_id=current_user.get_id()).first()
            ticker = ml.get_ticker(stock.ticker, '1d')
            png_graph = graphs.get_graph(ticker)
            my_file = f'{stock.ticker}TickDataPng'
            session[my_file] = my_file
            abs_path = os.path.abspath('flaskr/')
            path = f'{abs_path}home\\static\\dist\\images\\{my_file}.png'
            png_graph.savefig(path)

        return graphs.format_graph(png_graph)


@home_bp.route('/addTicker', methods=['GET', 'POST'])
@login_required
def add_ticker():
    if request.method == 'POST':
        data = request.get_json()
        res = ml.get_ticker(data['stockName'], '1d')

        if res.empty:
            print("get ticker failed")
            return False

        else:
            fav = True if data['favSize'] < 5 else False
            stock = Stock.query.filter(Stock.ticker == data['stockName']).first()
            if stock is None:
                stock = Stock(
                    ticker=data['stockName'],
                    user_id=current_user.get_id(),
                    is_fav=fav
                )
            db.session.add(stock)
            db.session.commit()
        return 'OK', 200
    else:
        stocks = Stock.query.filter(Stock.user_id == current_user.get_id(), Stock.is_fav).all()

        return render_template(
            'dashboard.jinja2',
            title='Smart Trader',
            description='user homepage',
            template='dashboard',
            current_user=current_user,
            stocks=stocks
        )


@home_bp.route('/deleteTicker', methods=['GET', 'POST'])
@login_required
def delete_ticker():
    if request.method == 'POST':
        data = request.get_json()
        name = data['stockName']
        stock = Stock.query.filter(Stock.user_id == current_user.get_id(), Stock.ticker == name).delete()
        db.session.commit()
        abs_path = os.path.abspath('flaskr/')
        abs_path = f'{abs_path}home\\static\\dist\\images\\'
        imgs = os.listdir(abs_path)
        for img in imgs:
            if name in img:
                os.remove(f'{abs_path}{img}')
                temp = img.split('.')
                session.pop(temp[0], None)

        return 'OK', 200
    else:
        stocks = Stock.query.filter(Stock.user_id == current_user.get_id(), Stock.is_fav).all()

        return render_template(
            'dashboard.jinja2',
            title='Smart Trader',
            description='user homepage',
            template='dashboard',
            current_user=current_user,
            stocks=stocks
        )


@home_bp.route('/createModel', methods=['POST'])
@login_required
def create_model():
    if request.method == 'POST':
        data = request.get_json()
        name = data['stockName']
        my_file = f'{name}Model'
        if my_file not in session:
            ticker = ml.get_ticker(name, '1d')
            ml.drop_date_for_model(ticker)
            ticker_train, ticker_test = ml.train_test_split(ticker)
            vals = ml.train_and_test_model(ticker_train, ticker_test)
            # TODO uncomment
            # if isinstance(vals, str):
            # return 'model accuracy is insufficient with training set; adjust inputs.'
            abs_path = os.path.abspath('flaskr/')
            path = f'{abs_path}home\\static\\dist\\models\\{my_file}.pkl'
            joblib.dump(vals[0], path)
            model_data = models.ModelData(name, vals[0], vals[1], vals[2])
            score = vals[3]
            session[f'{name}ModelScore'] = score
            session[f'{name}ModelPrediction'] = ml.predict_price(name, vals[0])
            session[my_file] = path
            # create graph and store
            path = f'{abs_path}home\\static\\dist\\images\\{my_file}.png'
            session[f'{my_file}Graph'] = path
            model_graph = model_data.get_graph()
            model_graph.savefig(path)

    return 'OK', 200


@home_bp.route('/graphModel.png', methods=['GET', 'POST'])
@login_required
def graph_model():
    if request.method == 'POST':
        data = request.get_json()
        name = data['stockName']
        session['currModel'] = session[f'{name}Model']
        session['currModelGraph'] = session[f'{name}ModelGraph']
        # TODO print score in javascript
        if f'{name}ModelScore' in session:
            score = session[f'{name}ModelScore']
            res = {"score": score}
            res = jsonify(res)
            return res, 200

        return 'OK', 200

    else:
        if 'currModel' in session:
            path = session['currModelGraph']
            return send_file(path, mimetype='image/png')
        else:
            message = {"response": 'The model does not exists'}
            message = jsonify(message)
            return message


@home_bp.route('/getPrediction', methods=['GET', 'POST'])
@login_required
def get_prediction():
    if request.method == 'POST':
        data = request.get_json()
        name = data['stockName']
        my_file = f'{name}Model'
        session['currModelName'] = name
        return 'OK', 200
    else:
        if 'currModelName' in session:
            name = session['currModelName']
            prediction = session[f'{name}ModelPrediction']
            prediction_obj = {"prediction": prediction}
            prediction_json = jsonify(prediction_obj)
            return prediction_json
        else:
            message = {"message": "there is no prediction available. please create model first."}
            message = jsonify(message)
            return message


@home_bp.route('/search.png', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        data = request.get_json()
        name = data['stockName']
        my_file = f'{name}TickDataPng'
        session['searchRes'] = data['stockName']
        session[my_file] = my_file
        ticker = ml.get_ticker(name, '1d')
        png_graph = graphs.get_graph(ticker)
        my_file = f'{name}TickDataPng'
        session[my_file] = my_file
        abs_path = os.path.abspath('flaskr/')
        path = f'{abs_path}home\\static\\dist\\images\\{my_file}.png'
        png_graph.savefig(path)
        message = 'stock was found and graphed with default'
        message = jsonify(message)
        return message, 200
    else:
        if 'searchRes' in session:
            name = session['searchRes']
            abs_path = os.path.abspath('flaskr/')
            print(abs_path)
            my_file = f'{name}TickDataPng'
            path = f'{abs_path}home\\static\\dist\\images\\{my_file}.png'
            return send_file(path, mimetype='image/png')
