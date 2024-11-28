import pandas as pd
import numpy as np
import tti.indicators as ti
import inspect
import warnings

warnings.filterwarnings('ignore')

def get_dirty_5min(df=initial_btc_data, visualize=False):
    df_copy = df.copy()
    df_copy.Date = pd.to_datetime(df_copy.Date)
    df_copy.rename(columns={
                            "Date": "date", 
                            "Open": "open", 
                            "High": "high", 
                            "Low": "low", 
                            "Close": "close", 
                            "Volume BTC": "volume"
                            }, inplace=True)
    new_df = df_copy.drop(["Timestamp", "Symbol", "Volume USD"], axis=1)
    new_df.set_index("date", inplace=True)
    df_5min = new_df.resample('5T').agg({
                                        'open': 'first',
                                        'high': 'max',
                                        'low': 'min',
                                        'close': 'last',
                                        'volume': 'sum'
                                        })
    df_5min_inter = df_5min.copy()
    df_5min_inter[["open", "close", "high", "low"]] = df_5min_inter[["open", "close", "high", "low"]].interpolate(method='linear') 
    df_5min_inter = df_5min_inter.iloc[1:]
    dirty_df = generate_indicators(df_5min_inter)
    if visualize == True:
        visualize_interpolation(dirty_df)
    return dirty_df

def clean_dirty_5min(df=dirty_df):
    data_dirty_copy = df.copy()
    issues = data_dirty_copy[data_dirty_copy.columns[data_dirty_copy.isna().sum() > 0]]
    too_much_nan = issues.columns[issues.isna().sum() >= 100000]
    data_dirty_copy = data_dirty_copy.drop(too_much_nan, axis=1)
    interpolate_nan = data_dirty_copy[data_dirty_copy.columns[data_dirty_copy.isna().sum() <= 100000]].columns
    data_inter = data_dirty_copy.copy()
    data_inter[interpolate_nan] = data_inter[interpolate_nan].interpolate(method="linear")
    data_inter.fillna(method='ffill', inplace=True)
    data_inter = data_inter.iloc[70:]
    data_inter = data_inter.drop(['emv', 'mfi', 'vrc'], axis=1)
    data_inter.to_csv("clean_5min.csv", index=True)
    
def visualize_interpolation(df=clean_df): #FIXME
    
    import matplotlib.pyplot as plt 

    fig, ax = plt.subplots()
    plot_data = df.loc["2018-11-01":"2019-01-01"]
    ax.plot(plot_data.index, plot_data["open"])
    plt.xticks(rotation=45)
    plt.show()

def process_cleaned_data():
    btc_data = pd.read_csv('clean_5min.csv', header=0, index_col=0)
    btc_data_copy_v1 = btc_data.copy()
    btc_data_copy_v1['date'] = pd.to_datetime(btc_data_copy_v1['date'])
    btc_data_copy_v1 = btc_data_copy_v1.set_index('date')
    btc_data_copy_v1['target_label'] = btc_data_copy_v1['close'].diff(-1).apply(lambda x: 1 if x <= 0 else -1)
    btc_data_copy_v1 = btc_data_copy_v1[:-1]
    btc_data_copy_targets = btc_data_copy_v1.target_label
    btc_data_copy_features = btc_data_copy_v1[['open', 'high', 'low', 'close', 'volume', 'dpo', 'dema', 'ma-simple', 'macd', 'sar', 'rsi', 'smi', 'cci', 'cmo', 'middle_band', 'upper_band', 'lower_band', 'sd', 'obv', 'tsf']]
    btc_data_copy_features['ma_dpo'] = btc_data_copy_features['dpo'].rolling(window=5).mean()
    btc_data_copy_features['ma_dpo'] = btc_data_copy_features['ma_dpo'].interpolate(method='cubic')
    btc_data_copy_features = btc_data_copy_features.drop('dpo', axis=1)
    return btc_data_copy_features, btc_data_copy_targets

def generate_indicators(df):
    
    ''' makes new features based on OHLCV data'''
    
    combined_df = df.copy()
    
    indicator_classes = [cls for _, cls in inspect.getmembers(ti, inspect.isclass)]
    
    for indicator_class in indicator_classes:
        try:
            indicator = indicator_class(input_data=df)
            indicator_data = indicator.getTiData()
            combined_df = combined_df.join(indicator_data, how='left')
        except Exception as e:
            pass
            
    combined_df['target_label'] = combined_df['close'].diff(-1).apply(lambda x: 1 if x <= 0 else -1)
    
    return combined_df

def preprocess_data(df=initial_btc_data, visualize=False):
    dirty_df = get_dirty_5min(df, visualize)
    clean_dirty_5min(dirty_df)
    btc_data_copy_features, btc_data_copy_targets = process_cleaned_data()
    return btc_data_copy_features, btc_data_copy_targets