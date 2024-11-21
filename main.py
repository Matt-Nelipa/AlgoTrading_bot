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

initial_btc_data = pd.read_csv('...') # raw btc data from Kaggle
clean_df = preprocess_data(initial_btc_data)
