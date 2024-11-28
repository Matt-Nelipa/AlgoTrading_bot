# if __name__ == __main__ - почитать про это

import numpy as np
import pandas as pd
import optuna
from optuna.samplers import TPESampler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
from sklearn.decomposition import PCA
import lightgbm as lgb
import time
from api_keys import api_public, api_secret
from datetime import datetime
from pybit.unified_trading import HTTP
import tti.indicators as ti
import inspect
import warnings
import matplotlib.pyplot as plt
from tenacity import retry, stop_after_attempt, wait_fixed
from preprocessing import preprocess_data
from bayesian_optimization import tune_parameters

initial_btc_data = pd.read_csv('...') # raw btc data from Kaggle
btc_data_copy_features, btc_data_copy_targets = preprocess_data(initial_btc_data)
params = tune_parameters()
dtrain = lgb.Dataset(btc_data_copy_features, label=btc_data_copy_targets, feature_name=list(btc_data_copy_features.columns))
tuned_model = lgb.train(params, dtrain)
api_key_ = api_public
api_secret_ = api_secret
session = HTTP(
    demo=True,
    api_key=api_key_,
    api_secret=api_secret_
)
date_list = []
probability_list = []
price_list = []