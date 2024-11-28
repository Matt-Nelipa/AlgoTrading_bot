@retry(stop=stop_after_attempt(5), wait=wait_fixed(10))
def get_wallet_balance_with_retry(session, accountType='UNIFIED', coin='BTC'):
    return session.get_wallet_balance(accountType=accountType, coin=coin)

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

def get_clean_ohlcv_data(symbol="BTCUSDT", interval=5):
    
    ''' extracts OHLCV data from Bybit for the last 5 minutes'''
    
    end_time = int(datetime.now().timestamp())  # Current time in seconds
    start_time = end_time - (5 * 60)  # time 5 min ago in seconds
    try:
        response = session.get_kline(
            category="spot",
            symbol=symbol,
            interval=str(interval),
            start=start_time * 1000,  # start_time to milliseconds
            end=end_time * 1000       # end_time to milliseconds
        )

        kline = response['result']['list'][0]
        ohlcv_data = {
                    "date": datetime.fromtimestamp(int(kline[0]) / 1000),
                    "open": float(kline[1]),
                    "high": float(kline[2]),
                    "low": float(kline[3]),
                    "close": float(kline[4]),
                    "volume": float(kline[5])
                    }
        
        df = pd.DataFrame(ohlcv_data.items()).T
        df.columns = df.iloc[0]
        df = df.iloc[1:].set_index('date')
        df = df.astype({
            'open':'Float64',
            'high':'Float64',
            'low':'Float64',
            'close':'Float64',
            'volume':'Float64'
        })
        return df
    except Exception as e:
        print("Error extracting data:", e)

def input_data_preprocessing():
    
    ''' combines previous OHLCV data with the newest one and processes it'''
    
    new_ohlcv_row = get_clean_ohlcv_data()
    last_55_rows_df = btc_data_copy_v1.iloc[-300:, :5]
    ohlcv_data = pd.concat([last_55_rows_df, new_ohlcv_row], axis=0)
    featured_data = generate_indicators(ohlcv_data)
    featured_data = featured_data.drop(['adl', 'cmf', 'emv_ma', 'emv', 'mfi', 'vrc', 'target_label'], axis=1)
    nan = featured_data[featured_data.columns[featured_data.isna().sum() > 0]].columns
    featured_data[nan] = featured_data[nan].fillna(featured_data[nan].rolling(window=50, min_periods=1).mean())
    featured_data = featured_data[['open', 'high', 'low', 'close', 'volume', 'dpo', 'dema', 'ma-simple', 'macd', 'sar', 'rsi', 'smi', 'cci', 'cmo', 'middle_band', 'upper_band', 'lower_band', 'sd', 'obv', 'tsf']]
    featured_data['ma_dpo'] = featured_data['dpo'].rolling(window=5).mean()
    featured_data['ma_dpo'] = featured_data['ma_dpo'].interpolate(method='cubic')
    featured_data = featured_data.drop('dpo', axis=1)
    return featured_data.iloc[[-1]]

def get_bitcoin_signal():
    
    '''ohlcv_data processing, features generation, 
    PCA application and model prediction'''
    
    preprocessed_data = input_data_preprocessing()
    y_pred = tuned_model.predict(preprocessed_data)
    last_btc_price = preprocessed_data['close'].iloc[-1]
    last_date = preprocessed_data.index[-1]
    # FIXME продумать логику добавления новых данных в исходные датасеты (зазписать в .csv)
    return (y_pred, last_btc_price, last_date)


def place_order(order_side: str, amount): #FIXME
    
    '''makes a "buy" or "sell" order'''
    
    try:
        order = session.place_order(
                                    category="spot",
                                    symbol="BTCUSDT",
                                    side=order_side, # Buy or Sell
                                    orderType="Market",
                                    qty=str(amount), # BTC value for Sell and USDT value for Buy
                                    marketunit="quoteCoin",
                                    timeInForce="IOC",
                                    isLeverage=0,
                                    orderFilter="Order"
                                    )
        print(f"{"Buy order" if order_side=="Buy" else "Sell order"} executed:", order)
    except Exception as e:
        print("Error making an order:", e)

def trading_bot(threshold=0.7, amount=1000):
    while True:
        probability, last_btc_price, last_date = get_bitcoin_signal()
        date_list.append(last_date)
        probability_list.append(probability)
        price_list.append(last_btc_price)
        btc_balance_in_usdt = float(get_wallet_balance_with_retry(session)['result']['list'][0]['coin'][0]['usdValue'])
        btc_balance_in_btc = float(get_wallet_balance_with_retry(session)['result']['list'][0]['coin'][0]['walletBalance'][:6])
        usdt_balance = float(get_wallet_balance_with_retry(session, coin='USDT')['result']['list'][0]['coin'][0]['usdValue'])
        if probability >= threshold and btc_balance_in_usdt > 100:
            print(f'Hold your tokens! Price increase probability: {probability[0]:.3f}')
        elif probability >= threshold and btc_balance_in_usdt <= 100:
            print(f"Buy signal! Price increase probability: {probability[0]:.3f}")
            place_order("Buy", amount)
        elif probability <= threshold and btc_balance_in_usdt > 100:
            print(f"Sell signal! Price increase probability: {probability[0]:.3f}")
            place_order("Sell", btc_balance_in_btc)
        else:
            print(f"Wait for a better opportunity. Price increase probability: {probability[0]:.3f}")
        
        btc_balance_in_usdt = float(get_wallet_balance_with_retry(session)['result']['list'][0]['coin'][0]['usdValue'])
        usdt_balance = float(get_wallet_balance_with_retry(session, coin='USDT')['result']['list'][0]['coin'][0]['usdValue'])
        print(f'Current BTC price: {last_btc_price}',
              f'BTC balance in USD: {btc_balance_in_usdt}',
              f'USDT balance: {usdt_balance}', sep='\n')    
        time.sleep(300)  # Checkout every 5 min