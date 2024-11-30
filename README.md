# AlgoTrading_bot

# **AlgoTrading bot**
This project implements an algorithmic trading bot based on gradient boosting, which gives an output probability that the market will go up. 
The data was found on Kaggle (**link**). Data processing was done using numpy and pandas, feature engineering using [*tti library*](https://github.com/vsaveris/trading-technical-indicators). *LightGBM* was used to compile the model, and *scikit-learn* was used to train and validate the model. Bayesian optimization was used for  hyperparameters tuning of the model and the implementation was done using *optuna*. The trading robot is connected via API to the ByBit exchange using *pybit*. The actions of the bot are logged, and data on the time of actions, bitcoin value and its growth probability are stored in the dataframe when the bot stops working. A *Dockerfile* has been created for further implementation via Docker to make the project reproducible. 
- **main.py** contains the basic procedures for executing the code
- **api_keys.py** contains public and private keys for connecting the bot to the exchange (must be created for correct operation. There should be two variables of "str" type inside: api_public and api_secret)
- **preprocessing.py** contains a procedure for processing data received from the exchange every 5 minutes.
- **bayesian_optimization.py** contains the implementation of Bayesian optimization of gradient boosting hyperparameters
- **bot_initialize.py** contains the logic of trading bot operation
- **notebooks** directory contains *.ipynb* files, where you can examine some actions in more detail (in particular, feature importance, some data visualization, etc.)
- **Dockerfile** contains instructions for further Docker image build
- **requirements.txt** contains necessary dependencies for correct code operation

Developers: [Matvei Nelipa](https://github.com/Matt-Nelipa) and [Andrei Chertkov](https://github.com/andrewch28)