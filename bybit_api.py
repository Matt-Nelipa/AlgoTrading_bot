import requests
import time
import hashlib
import hmac
import json
import pandas as pd 

# Ваши API ключи
api_key = 'IZA9qllveLmXKTi51l'  # Замените на свой API ключ
secret_key = 'N6cqqBsqCNLUZXAb6RoAmaxoOwbcxvAMHDqY'  # Замените на свой Secret Key


# URL для Bybit Testnet API v5
base_url = 'https://api-testnet.bybit.com'
endpoint = '/v5/market/recent-trade'

# Параметры запроса
params = {
    'symbol': 'BTCUSDT',  # Торговая пара
    'limit': 10            # Количество возвращаемых записей
}

# Выполнение GET запроса к API
response = requests.get(base_url + endpoint, params=params)

# Проверка ответа
if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data["result"]["list"]).drop(["execId"], axis=1)
    print(df)
    #print(json.dumps(data, indent=4))
else:
    print(f"Ошибка: {response.status_code}, {response.text}")