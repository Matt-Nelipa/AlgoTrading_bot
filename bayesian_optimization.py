import numpy as np
import pandas as pd
import optuna
from optuna.samplers import TPESampler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
from sklearn.decomposition import PCA
import lightgbm as lgb

def objective(trial):

    param = {
        "objective": "binary",
        "metric": "auc",
        "verbosity": -1,
        "n_jobs": -1,
        "random_state": 42,
        "is_unbalance": True,
        "subsample": 1.0,
        "boosting_type": 'gbdt',
        'n_estimators': trial.suggest_int("n_estimators", 100, 2000),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.2, log=True),
        "lambda_l1": trial.suggest_float("lambda_l1", 1e-1, 10.0, log=True),
        "lambda_l2": trial.suggest_float("lambda_l2", 1e-1, 10.0, log=True),
        "num_leaves": trial.suggest_int("num_leaves", 10, 50),
        "feature_fraction": trial.suggest_float("feature_fraction", 0.1, 0.5),
        "bagging_fraction": trial.suggest_float("bagging_fraction", 0.2, 0.8),
        "bagging_freq": trial.suggest_int("bagging_freq", 1, 3),
        "min_child_samples": trial.suggest_int("min_child_samples", 5, 100),
        "max_depth": trial.suggest_int('max_depth', 1, 5),
        'max_bin': trial.suggest_int('max_bin', 100, 150),
        'min_data_in_leaf': trial.suggest_int('min_data_in_leaf', 20, 150),
    }
    
    dtrain = lgb.Dataset(X_train, label=y_train)

    gbm = lgb.train(param, dtrain)
    y_pred = gbm.predict(X_test)
    auc = roc_auc_score(y_test, y_pred)
    return auc

def tune_parameters():
    tscv = TimeSeriesSplit(n_splits=5)
    sampler_complex = TPESampler(n_startup_trials=10, seed=42)
    study_complex = optuna.create_study(direction='maximize', sampler=sampler_complex)

    for train_index, test_index in tscv.split(btc_data_copy_features):
        X_train, X_test = btc_data_copy_features.iloc[train_index], btc_data_copy_features.iloc[test_index]
        y_train, y_test = btc_data_copy_targets.iloc[train_index], btc_data_copy_targets.iloc[test_index]
        study_complex.optimize(objective, n_trials=10)
    
    params = study_complex.best_params | {
                                        "objective": "binary",
                                        "metric": "auc",
                                        "verbosity": -1,
                                        "n_jobs": -1,
                                        "random_state": 42,
                                        "is_unbalance": True,
                                        "subsample": 1.0,
                                        }
    return params