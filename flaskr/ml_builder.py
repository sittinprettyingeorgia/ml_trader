import yfinance as yf
import pandas as pd
import numpy as np
import datetime
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from typing import Tuple

# aws sign in link
# https://682882423375.signin.aws.amazon.com/console
# bucket name = admin-models

# apply scaling and missing value fills
stk_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('std_scaler', StandardScaler()),
])


# TODO if the ticker has a history less than 5 years we need to pool data from other tickers with like data
# TODO like data will be considered as similiar float amounts and price ranges.

def get_ticker(ticker, my_interval, start_date=None, end_date=None):
    if start_date is None and end_date is None:
        end_date = datetime.datetime.today()
        start_date = end_date - datetime.timedelta(days=365)

    my_ticker = yf.Ticker(ticker)
    # ticker_hist = my_ticker.history(interval=my_interval, start=start_date, end=end_date, actions=False)
    ticker_hist = my_ticker.history(interval=my_interval, period='5y', actions=False)
    ticker_hist['Close'] = ticker_hist['Close'].shift(-1)
    ticker_hist = ticker_hist.iloc[:-1, :]
    if ticker_hist is str:
        my_ticker = yf.Ticker(ticker)
        # ticker_hist = my_ticker.history(interval=my_interval, start=start_date, end=end_date, actions=False)
        ticker_hist = my_ticker.history(interval=my_interval, period='5y', actions=False)
        ticker_hist['Close'] = ticker_hist['Close'].shift(-1)
        ticker_hist = ticker_hist.iloc[:-1, :]

    return ticker_hist


def drop_date_for_model(ticker):
    ticker.reset_index(inplace=True)
    ticker.drop(columns='Date', inplace=True)


def train_test_split(stock_hist):
    # copy the data
    stock = stock_hist.copy()

    # scale volume to account for variations in volume for particular stocks
    stock['scaled_vol'] = (stock['Volume'] - stock['Volume'].min()) / (stock['Volume'].max() - stock['Volume'].min())

    # separate scaled volume into categories
    bin_vals = [0., 0.2, 0.4, 0.6, 0.8, 1]
    label_vals = [1, 2, 3, 4, 5]
    stock['vol_cat'] = pd.cut(stock['scaled_vol'], bins=bin_vals, labels=label_vals)

    # remove low count categories
    while (stock['vol_cat'].value_counts().tolist().count(1) > 0 or
           stock['vol_cat'].value_counts().tolist().count(0) > 0):
        stock['vol_cat'] = pd.cut(stock['scaled_vol'], bins=bin_vals, labels=label_vals)

        index_val = 1
        for index, val in stock['vol_cat'].value_counts().items():
            if val < 2:
                bin_vals.pop(index_val)
                index_val = index_val - 1
                label_vals.pop()

            index_val = index_val + 1

    # adapt categories to better suite scaled_vol
    bin_val = 0
    count = 1
    cat_size = max(bin_vals) / 5
    temp_vals = []
    label_vals = []

    while bin_val <= max(bin_vals):
        temp_vals.append(bin_val)
        label_vals.append(count)
        bin_val = bin_val + cat_size

        if count < 5:
            count = count + 1

    bin_vals = temp_vals

    # make sure the type passed from mode function is an integer for bin labels
    mode = int(stock['vol_cat'].mode())
    stock['vol_cat'] = stock['vol_cat'].fillna(mode)

    # create stratified train and test set
    split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    for train_index, test_index in split.split(stock, stock['vol_cat']):
        stock_train_set = stock.loc[train_index]
        stock_test_set = stock.loc[test_index]

    # remove 'vol_cat' to return train and test data to original state.
    for set_ in (stock_train_set, stock_test_set):
        set_.drop(['vol_cat', 'scaled_vol'], axis=1, inplace=True)

    return stock_train_set, stock_test_set


def train_and_test_model(stock_train: pd.DataFrame, stock_test: pd.DataFrame) -> Tuple[LinearRegression, np.ndarray,
                                                                                       pd.Series, float]:
    print(f'type of stock train ={type(stock_train)} ')
    print(f'type of stock test = {type(stock_test)}')
    # isolate independent and dependent variables

    stock_x = stock_train.drop(['Close', 'Low'], axis=1)
    stock_y = stock_train['Close'].copy()

    # reshape if dealing with single variable in stock_x
    # stock_x = np.array(stock_x).reshape((len(stock_x), 1))

    # train the model
    stock_prepared_x = stk_pipeline.fit_transform(stock_x)
    lin_reg = LinearRegression()
    lin_reg.fit(stock_prepared_x, stock_y)
    stock_predictions = lin_reg.predict(stock_prepared_x)

    # get mean square error and root mean square error
    # calculate error between predicted y values and actual y values
    mse = mean_squared_error(stock_y, stock_predictions)
    rmse = np.sqrt(mse)

    # get mse and rmse of cross_val split training
    scores = cross_val_score(lin_reg, stock_prepared_x, stock_y, scoring='neg_mean_squared_error', cv=10)
    rmse_scores = np.sqrt(-scores)
    print(f'rmse value ={rmse}')
    # check if model accuracy is sufficient
    # then verify model with test set

    # if rmse > 0.4:
    # return 'model accuracy is insufficient with training set; adjust inputs.'

    final_model = lin_reg
    print(f'type of final model ={type(final_model)}')

    x_test = stock_test.drop(['Close', 'Low'], axis=1)
    y_test = stock_test['Close'].copy()
    print(f'type of y_test ={type(y_test)}')

    # x_test = np.array(x_test).reshape((len(x_test), 1))

    x_test_prepared = stk_pipeline.transform(x_test)
    final_score = final_model.score(stock_prepared_x, stock_y)
    print(f'the final score for the model is {final_score}')
    final_predictions = final_model.predict(x_test_prepared)
    print(f'type of final predictions ={type(final_predictions)}')
    final_mse = mean_squared_error(y_test, final_predictions)
    final_rmse = np.sqrt(final_mse)

    # if final_rmse > 0.4:
    # return 'model accuracy is insufficient with testing set; adjust inputs'

    return final_model, final_predictions, y_test, final_score


def predict_price(ticker, model):
    final_model = model

    date = datetime.date.today()
    if date.weekday() > 4:
        subtract = date.weekday() - 4
        date = date - datetime.timedelta(days=subtract)

    date_2 = date + datetime.timedelta(days=1)
    date = date - datetime.timedelta(days=1)
    date_start = date.strftime("%Y-%m-%d")
    date_end = date_2.strftime("%Y-%m-%d")

    data = get_ticker(ticker, '1d', date_start, date_end)

    x_test = data.drop(['Close', 'Low'], axis=1)
    y_test = data['Close'].copy()

    x_test_prepared = stk_pipeline.transform(x_test)

    final_predictions = final_model.predict(x_test_prepared)
    final_mse = mean_squared_error(y_test, final_predictions)
    final_rmse = np.sqrt(final_mse)

    return final_predictions[0]
